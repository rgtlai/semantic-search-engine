import logging
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models
from app.utils.config import settings
from app.utils.embeddings import get_embedding_service
from app.models.response import DocumentSource

logger = logging.getLogger(__name__)

class QdrantService:
    """
    Qdrant vector database service for document retrieval.
    Based on Module_1 implementation.
    """
    
    def __init__(self):
        self.client = self._initialize_client()
        self.embedding_service = get_embedding_service()
        
        # Collection mapping from Module_1
        self.collections = {
            "OPENAI_QUERY": "opnai_data",
            "10K_DOCUMENT_QUERY": "10k_data"
        }
    
    def _initialize_client(self) -> QdrantClient:
        """Initialize Qdrant client."""
        try:
            if settings.qdrant_url.startswith("http"):
                # Remote Qdrant instance
                client = QdrantClient(
                    url=settings.qdrant_url,
                    api_key=settings.qdrant_api_key if settings.qdrant_api_key else None
                )
            else:
                # Local Qdrant instance (file path)
                client = QdrantClient(path=settings.qdrant_url)
            
            logger.info(f"Successfully connected to Qdrant at {settings.qdrant_url}")
            return client
            
        except Exception as e:
            logger.error(f"Failed to initialize Qdrant client: {e}")
            raise
    
    def search_documents(self, query: str, collection_type: str, limit: int = 3) -> List[DocumentSource]:
        """
        Search for relevant documents in the specified collection.
        
        Args:
            query: Search query
            collection_type: Type of collection (OPENAI_QUERY or 10K_DOCUMENT_QUERY)
            limit: Number of results to return
            
        Returns:
            List of DocumentSource objects
        """
        try:
            # Get collection name
            collection_name = self.collections.get(collection_type)
            if not collection_name:
                logger.error(f"Invalid collection type: {collection_type}")
                return []
            
            # Generate query embedding
            query_embedding = self.embedding_service.get_text_embeddings(query)
            
            # Perform similarity search
            search_results = self.client.query_points(
                collection_name=collection_name,
                query=query_embedding.tolist(),
                limit=limit
            )
            
            # Convert results to DocumentSource objects
            documents = []
            for point in search_results.points:
                doc_source = DocumentSource(
                    content=point.payload.get('content', ''),
                    metadata=point.payload,
                    score=point.score if hasattr(point, 'score') else None,
                    source_type=collection_type.lower()
                )
                documents.append(doc_source)
            
            logger.info(f"Found {len(documents)} documents in {collection_name}")
            return documents
            
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return []
    
    def get_collection_info(self, collection_type: str) -> Dict[str, Any]:
        """Get information about a collection."""
        try:
            collection_name = self.collections.get(collection_type)
            if not collection_name:
                return {"error": f"Invalid collection type: {collection_type}"}
            
            info = self.client.get_collection(collection_name)
            return {
                "name": collection_name,
                "points_count": info.points_count,
                "vectors_count": info.vectors_count,
                "status": info.status
            }
            
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            return {"error": str(e)}
    
    def health_check(self) -> bool:
        """Check if Qdrant service is healthy."""
        try:
            # Try to list collections as a health check
            collections = self.client.get_collections()
            return True
        except Exception as e:
            logger.error(f"Qdrant health check failed: {e}")
            return False

# Global Qdrant service instance
qdrant_service = None

def get_qdrant_service() -> QdrantService:
    """Get global Qdrant service instance."""
    global qdrant_service
    if qdrant_service is None:
        qdrant_service = QdrantService()
    return qdrant_service