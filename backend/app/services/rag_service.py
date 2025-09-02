import time
import logging
from typing import Dict, Any, List
from openai import OpenAI, OpenAIError
from app.models.query import QueryType, RouterResponse
from app.models.response import SearchResponse, DocumentSource
from app.services.router_service import get_router_service
from app.services.qdrant_service import get_qdrant_service
from app.services.web_search_service import get_web_search_service
from app.services.cache_service import get_cache_service
from app.utils.config import settings

logger = logging.getLogger(__name__)

class RAGService:
    """
    Main RAG service that orchestrates the entire pipeline.
    Combines routing, retrieval, caching, and generation.
    """
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.openai_api_key)
        self.router_service = get_router_service()
        self.qdrant_service = get_qdrant_service()
        self.web_search_service = get_web_search_service()
        self.cache_service = get_cache_service()
        
        # Route function mapping
        self.route_handlers = {
            QueryType.OPENAI_QUERY: self._handle_document_query,
            QueryType.DOCUMENT_10K_QUERY: self._handle_document_query,
            QueryType.INTERNET_QUERY: self._handle_web_query
        }
    
    def process_query(self, query: str, allow_web_search: bool = True) -> SearchResponse:
        """
        Main entry point for processing user queries.
        Implements the full agentic RAG pipeline.
        """
        start_time = time.time()
        
        try:
            # Step 1: Check semantic cache first
            cached_response, cache_metrics = self.cache_service.search_cache(query)
            
            if cached_response:
                # Cache hit - return cached response
                return SearchResponse(
                    answer=cached_response.get('answer', ''),
                    sources=cached_response.get('sources', []),
                    query_type=QueryType(cached_response.get('query_type', 'INTERNET_QUERY')),
                    cache_metrics=cache_metrics,
                    processing_time=time.time() - start_time
                )
            
            # Step 2: Route the query to determine processing type
            routing_response = self.router_service.route_query(query)
            logger.info(f"Query routed to: {routing_response.action}")
            
            # Step 3: Handle web search restriction
            if routing_response.action == QueryType.INTERNET_QUERY and not allow_web_search:
                return SearchResponse(
                    answer="Web search is disabled. Please enable it to search for external information.",
                    sources=[],
                    query_type=routing_response.action,
                    cache_metrics=cache_metrics,
                    processing_time=time.time() - start_time
                )
            
            # Step 4: Process the query based on routing decision
            handler = self.route_handlers.get(routing_response.action)
            if not handler:
                raise ValueError(f"No handler found for query type: {routing_response.action}")
            
            result = handler(query, routing_response.action)
            
            # Step 5: Create response object
            response = SearchResponse(
                answer=result.get('answer', ''),
                sources=result.get('sources', []),
                query_type=routing_response.action,
                cache_metrics=cache_metrics,
                processing_time=time.time() - start_time
            )
            
            # Step 6: Store in cache for future use
            response_data = {
                'answer': response.answer,
                'sources': [source.dict() for source in response.sources],
                'query_type': response.query_type.value,
                'routing_reason': routing_response.reason
            }
            self.cache_service.store_response(query, response_data)
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return SearchResponse(
                answer=f"Error processing query: {str(e)}",
                sources=[],
                query_type=QueryType.INTERNET_QUERY,
                cache_metrics=None,
                processing_time=time.time() - start_time
            )
    
    def _handle_document_query(self, query: str, query_type: QueryType) -> Dict[str, Any]:
        """
        Handle queries that require document retrieval from Qdrant.
        Based on Module_1 implementation.
        """
        try:
            # Retrieve relevant documents
            documents = self.qdrant_service.search_documents(
                query=query,
                collection_type=query_type.value,
                limit=3
            )
            
            if not documents:
                return {
                    "answer": "No relevant documents found in the database.",
                    "sources": []
                }
            
            # Extract content for RAG generation
            context_chunks = [doc.content for doc in documents]
            
            # Generate response using RAG
            answer = self._generate_rag_response(query, context_chunks)
            
            return {
                "answer": answer,
                "sources": documents
            }
            
        except Exception as e:
            logger.error(f"Error in document query handling: {e}")
            return {
                "answer": f"Error retrieving documents: {str(e)}",
                "sources": []
            }
    
    def _handle_web_query(self, query: str, query_type: QueryType) -> Dict[str, Any]:
        """Handle queries that require web search."""
        try:
            # Perform web search
            search_result = self.web_search_service.search_internet(query)
            
            # Create document source for web result
            web_source = DocumentSource(
                content=search_result.get('answer', ''),
                metadata={
                    'search_query': query,
                    'source': 'ares_api',
                    'full_response': search_result.get('full_response', {})
                },
                source_type='web_search'
            )
            
            return {
                "answer": search_result.get('answer', ''),
                "sources": [web_source]
            }
            
        except Exception as e:
            logger.error(f"Error in web query handling: {e}")
            return {
                "answer": f"Error performing web search: {str(e)}",
                "sources": []
            }
    
    def _generate_rag_response(self, query: str, context: List[str]) -> str:
        """
        Generate response using retrieved context.
        Based on Module_1 RAG implementation.
        """
        try:
            # Build RAG prompt
            rag_prompt = f"""
            Based on the given context, answer the user query: {query}
            
            Context:
            {chr(10).join(context)}
            
            Please provide a comprehensive answer using the provided context and include references 
            to the relevant information sources where appropriate.
            """
            
            # Generate response using GPT-4
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "system", "content": rag_prompt}]
            )
            
            return response.choices[0].message.content
            
        except OpenAIError as e:
            logger.error(f"OpenAI API error in RAG generation: {e}")
            return f"Error generating response: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error in RAG generation: {e}")
            return f"Error generating response: {str(e)}"
    
    def process_sub_queries(self, query: str, allow_web_search: bool = True) -> SearchResponse:
        """
        Process complex queries by dividing them into sub-queries.
        Implements sub-query division from assignment requirements.
        """
        start_time = time.time()
        
        try:
            # Divide query into sub-questions
            sub_query_response = self.router_service.divide_sub_queries(query)
            sub_questions = sub_query_response.subQuestions
            
            if len(sub_questions) <= 1:
                # Single query - process normally
                return self.process_query(query, allow_web_search)
            
            # Process each sub-query
            all_results = []
            all_sources = []
            
            logger.info(f"Processing {len(sub_questions)} sub-queries")
            
            for i, sub_query in enumerate(sub_questions):
                logger.info(f"Processing sub-query {i+1}: {sub_query}")
                sub_result = self.process_query(sub_query, allow_web_search)
                all_results.append(f"Sub-question {i+1}: {sub_query}\nAnswer: {sub_result.answer}")
                all_sources.extend(sub_result.sources)
            
            # Combine results
            combined_answer = "\n\n".join(all_results)
            
            return SearchResponse(
                answer=combined_answer,
                sources=all_sources,
                query_type=QueryType.INTERNET_QUERY,  # Mixed query type
                cache_metrics=None,
                processing_time=time.time() - start_time
            )
            
        except Exception as e:
            logger.error(f"Error processing sub-queries: {e}")
            return self.process_query(query, allow_web_search)

# Global RAG service instance
rag_service = None

def get_rag_service() -> RAGService:
    """Get global RAG service instance."""
    global rag_service
    if rag_service is None:
        rag_service = RAGService()
    return rag_service