import faiss
import json
import numpy as np
import time
import logging
from typing import Optional, Tuple, List, Dict, Any
from app.utils.embeddings import get_embedding_service
from app.utils.config import settings
from app.models.query import CacheMetrics
from pathlib import Path

logger = logging.getLogger(__name__)

class SemanticCacheService:
    """
    Semantic caching implementation based on Module_3.
    Uses FAISS for similarity search and persistent JSON storage.
    """
    
    def __init__(self, cache_file: str = None, clear_on_init: bool = False):
        # Initialize FAISS index with Euclidean distance (L2)
        self.index = faiss.IndexFlatL2(settings.embedding_dimension)
        
        # Initialize embedding service
        self.embedding_service = get_embedding_service()
        
        # Distance threshold for cache hits
        self.threshold = settings.cache_similarity_threshold
        
        # Cache file path
        self.cache_file = cache_file or settings.cache_file_path
        
        # Initialize cache structure
        if clear_on_init:
            self.clear_cache()
        else:
            self.load_cache()
    
    def clear_cache(self):
        """Clear in-memory cache, reset FAISS index, and overwrite cache file."""
        self.cache = {
            'questions': [],
            'embeddings': [],
            'answers': [],
            'response_data': [],
            'timestamps': []
        }
        self.index = faiss.IndexFlatL2(settings.embedding_dimension)
        self.save_cache()
        logger.info("Semantic cache cleared")
    
    def load_cache(self):
        """Load existing cache or initialize empty structure."""
        try:
            with open(self.cache_file, 'r') as file:
                self.cache = json.load(file)
            
            # Rebuild FAISS index from stored embeddings
            if self.cache.get('embeddings'):
                embeddings_array = np.array(self.cache['embeddings'], dtype=np.float32)
                self.index.add(embeddings_array)
            
            logger.info(f"Loaded cache with {len(self.cache.get('questions', []))} entries")
            
        except FileNotFoundError:
            self.cache = {
                'questions': [],
                'embeddings': [],
                'answers': [],
                'response_data': [],
                'timestamps': []
            }
            logger.info("Initialized new cache")
        except Exception as e:
            logger.error(f"Error loading cache: {e}")
            self.cache = {
                'questions': [],
                'embeddings': [],
                'answers': [],
                'response_data': [],
                'timestamps': []
            }
    
    def save_cache(self):
        """Persist cache to disk."""
        try:
            # Ensure directory exists
            Path(self.cache_file).parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.cache_file, 'w') as file:
                json.dump(self.cache, file, indent=2, default=str)
                
        except Exception as e:
            logger.error(f"Error saving cache: {e}")
    
    def search_cache(self, question: str) -> Tuple[Optional[str], CacheMetrics]:
        """
        Search for cached response to similar question.
        
        Args:
            question: User query to search for
            
        Returns:
            Tuple of (cached_response, cache_metrics)
        """
        start_time = time.time()
        
        try:
            # Generate embedding for the question
            embedding = self.embedding_service.get_text_embeddings(question)
            embedding = embedding.reshape(1, -1).astype(np.float32)
            
            # Search for nearest neighbor
            if self.index.ntotal > 0:
                distances, indices = self.index.search(embedding, 1)
                
                if indices[0][0] != -1 and distances[0][0] <= self.threshold:
                    # Cache hit
                    row_id = int(indices[0][0])
                    cached_response = self.cache['response_data'][row_id]
                    
                    similarity_score = 1.0 - distances[0][0]  # Convert distance to similarity
                    response_time = time.time() - start_time
                    
                    logger.info(f"Cache hit at row {row_id} with similarity {similarity_score:.3f}")
                    
                    metrics = CacheMetrics(
                        hit=True,
                        similarity_score=similarity_score,
                        response_time=response_time,
                        cache_size=len(self.cache['questions'])
                    )
                    
                    return cached_response, metrics
            
            # Cache miss
            response_time = time.time() - start_time
            metrics = CacheMetrics(
                hit=False,
                similarity_score=None,
                response_time=response_time,
                cache_size=len(self.cache['questions'])
            )
            
            return None, metrics
            
        except Exception as e:
            logger.error(f"Error searching cache: {e}")
            response_time = time.time() - start_time
            metrics = CacheMetrics(
                hit=False,
                similarity_score=None,
                response_time=response_time,
                cache_size=len(self.cache['questions'])
            )
            return None, metrics
    
    def store_response(self, question: str, response_data: Dict[str, Any]) -> bool:
        """
        Store new question-response pair in cache.
        
        Args:
            question: User query
            response_data: Complete response data to cache
            
        Returns:
            bool: Success status
        """
        try:
            # Generate embedding
            embedding = self.embedding_service.get_text_embeddings(question)
            
            # Add to cache
            self.cache['questions'].append(question)
            self.cache['embeddings'].append(embedding.tolist())
            self.cache['answers'].append(response_data.get('answer', ''))
            self.cache['response_data'].append(response_data)
            self.cache['timestamps'].append(time.time())
            
            # Add to FAISS index
            embedding_array = embedding.reshape(1, -1).astype(np.float32)
            self.index.add(embedding_array)
            
            # Save to disk
            self.save_cache()
            
            logger.info(f"Stored new cache entry. Cache size: {len(self.cache['questions'])}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing response in cache: {e}")
            return False
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "cache_size": len(self.cache.get('questions', [])),
            "total_entries": len(self.cache.get('questions', [])),
            "cache_file": self.cache_file,
            "threshold": self.threshold,
            "embedding_dimension": settings.embedding_dimension
        }

# Global cache service instance
cache_service = None

def get_cache_service() -> SemanticCacheService:
    """Get global cache service instance."""
    global cache_service
    if cache_service is None:
        cache_service = SemanticCacheService()
    return cache_service