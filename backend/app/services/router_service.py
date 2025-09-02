import json
import re
import logging
from openai import OpenAI, OpenAIError
from typing import Dict, Any
from app.models.query import RouterResponse, QueryType, SubQueryResponse
from app.utils.config import settings

logger = logging.getLogger(__name__)

class RouterService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        
    def route_query(self, user_query: str) -> RouterResponse:
        """
        Route query to appropriate handler based on content classification.
        Based on Module_1 implementation.
        """
        router_system_prompt = f"""
        As a professional query router, your objective is to correctly classify user input into one of three categories based on the source most relevant for answering the query:
        1. "OPENAI_QUERY": If the user's query appears to be answerable using information from OpenAI's official documentation, tools, models, APIs, or services (e.g., GPT, ChatGPT, embeddings, moderation API, usage guidelines).
        2. "10K_DOCUMENT_QUERY": If the user's query pertains to a collection of documents from the 10k annual reports, datasets, or other structured documents, typically for research, analysis, or financial content.
        3. "INTERNET_QUERY": If the query is neither related to OpenAI nor the 10k documents specifically, or if the information might require a broader search (e.g., news, trends, tools outside these platforms), route it here.

        Your decision should be made by assessing the domain of the query.

        Always respond in this valid JSON format:
        {{
            "action": "OPENAI_QUERY" or "10K_DOCUMENT_QUERY" or "INTERNET_QUERY",
            "reason": "brief justification",
            "answer": "AT MAX 5 words answer. Leave empty if INTERNET_QUERY"
        }}

        EXAMPLES:

        - User: "How to fine-tune GPT-3?"
        Response:
        {{
            "action": "OPENAI_QUERY",
            "reason": "Fine-tuning is OpenAI-specific",
            "answer": "Use fine-tuning API"
        }}

        - User: "Where can I find the latest financial reports for the last 10 years?"
        Response:
        {{
            "action": "10K_DOCUMENT_QUERY",
            "reason": "Query related to annual reports",
            "answer": "Access through document database"
        }}

        - User: "Top leadership styles in 2024"
        Response:
        {{
            "action": "INTERNET_QUERY",
            "reason": "Needs current leadership trends",
            "answer": ""
        }}

        - User: "What's the difference between ChatGPT and Claude?"
        Response:
        {{
            "action": "INTERNET_QUERY",
            "reason": "Cross-comparison of different providers",
            "answer": ""
        }}

        Strictly follow this format for every query, and never deviate.
        User: {user_query}
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "system", "content": router_system_prompt}]
            )

            task_response = response.choices[0].message.content
            json_match = re.search(r"\{.*\}", task_response, re.DOTALL)
            
            if not json_match:
                logger.error("No JSON found in router response")
                return RouterResponse(
                    action=QueryType.INTERNET_QUERY,
                    reason="Failed to parse router response",
                    answer=""
                )
            
            json_text = json_match.group()
            parsed_response = json.loads(json_text)
            
            return RouterResponse(
                action=QueryType(parsed_response["action"]),
                reason=parsed_response["reason"],
                answer=parsed_response.get("answer", "")
            )

        except OpenAIError as api_err:
            logger.error(f"OpenAI API error in routing: {api_err}")
            return RouterResponse(
                action=QueryType.INTERNET_QUERY,
                reason=f"OpenAI API error: {api_err}",
                answer=""
            )
        except json.JSONDecodeError as json_err:
            logger.error(f"JSON parsing error in routing: {json_err}")
            return RouterResponse(
                action=QueryType.INTERNET_QUERY,
                reason=f"JSON parsing error: {json_err}",
                answer=""
            )
        except Exception as err:
            logger.error(f"Unexpected error in routing: {err}")
            return RouterResponse(
                action=QueryType.INTERNET_QUERY,
                reason=f"Unexpected error: {err}",
                answer=""
            )

    def divide_sub_queries(self, user_query: str) -> SubQueryResponse:
        """
        Break down complex queries into sub-questions with improved logic.
        Handles various complex query patterns including:
        - Multiple questions with conjunctions (and, or)
        - Comparative queries
        - Sequential questions
        - Nested questions
        """
        sub_queries_prompt = f"""
        You are an expert query analyzer. Your task is to identify if a user query contains multiple distinct questions or information needs, and if so, break it down into focused sub-questions that can be answered independently.

        RULES:
        1. If the query is a single, focused question → return it as-is
        2. If the query contains multiple distinct information needs → break into separate sub-questions
        3. Each sub-question should be self-contained and answerable independently
        4. Preserve the original intent and context of each question
        5. Handle comparisons by creating separate questions for each entity being compared

        EXAMPLES:

        Query: "What is the revenue of Lyft in 2024?"
        → Single focused query, no division needed
        Response: {{"subQuestions": ["What is the revenue of Lyft in 2024?"]}}

        Query: "What is the revenue of Lyft in 2024 and what was Uber's revenue in 2021?"
        → Two distinct company/year combinations
        Response: {{"subQuestions": ["What is the revenue of Lyft in 2024?", "What was Uber's revenue in 2021?"]}}

        Query: "Compare the financial performance of Apple and Microsoft, and also tell me about the latest AI developments"
        → Three distinct information needs
        Response: {{"subQuestions": ["What is the financial performance of Apple?", "What is the financial performance of Microsoft?", "What are the latest AI developments?"]}}

        Query: "How do I use OpenAI's chat completions API and what are the pricing details?"
        → Two related but distinct questions
        Response: {{"subQuestions": ["How do I use OpenAI's chat completions API?", "What are the pricing details for OpenAI's API?"]}}

        Query: "What are the best programming languages for AI in 2024, their advantages, and which companies are using them?"
        → Three related information needs
        Response: {{"subQuestions": ["What are the best programming languages for AI in 2024?", "What are the advantages of these AI programming languages?", "Which companies are using these AI programming languages?"]}}

        IMPORTANT: Return ONLY a valid JSON object in this exact format:
        {{
            "subQuestions": ["question1", "question2", ...]
        }}

        Query: "{user_query}"
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "system", "content": sub_queries_prompt}],
                temperature=0.1  # Lower temperature for more consistent parsing
            )
            
            task_response = response.choices[0].message.content.strip()
            
            # Try to extract JSON from the response
            json_match = re.search(r"\{.*?\}", task_response, re.DOTALL)
            
            if json_match:
                json_text = json_match.group()
                parsed_response = json.loads(json_text)
                
                # Validate the response structure
                if "subQuestions" in parsed_response and isinstance(parsed_response["subQuestions"], list):
                    sub_questions = parsed_response["subQuestions"]
                    
                    # Filter out empty questions and ensure minimum quality
                    valid_questions = [q.strip() for q in sub_questions if q.strip() and len(q.strip()) > 10]
                    
                    if valid_questions:
                        logger.info(f"Divided query into {len(valid_questions)} sub-questions")
                        return SubQueryResponse(subQuestions=valid_questions)
                
            # Fallback: return original query if parsing fails
            logger.warning(f"Failed to parse sub-query response, using original query")
            return SubQueryResponse(subQuestions=[user_query])
                
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error in sub-query division: {e}")
            return SubQueryResponse(subQuestions=[user_query])
        except Exception as e:
            logger.error(f"Error in sub-query division: {e}")
            return SubQueryResponse(subQuestions=[user_query])

# Global router service instance
router_service = None

def get_router_service() -> RouterService:
    """Get global router service instance"""
    global router_service
    if router_service is None:
        router_service = RouterService()
    return router_service