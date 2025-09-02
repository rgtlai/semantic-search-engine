import numpy as np
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModel
import torch
from typing import Union, List
import logging

logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self, model_name: str = "nomic-ai/nomic-embed-text-v1.5"):
        """Initialize embedding service with Nomic AI model"""
        try:
            self.model_name = model_name
            self.tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
            self.model = AutoModel.from_pretrained(model_name, trust_remote_code=True)
            self.sentence_model = SentenceTransformer(model_name, trust_remote_code=True)
            logger.info(f"Successfully loaded embedding model: {model_name}")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise
    
    def get_text_embeddings(self, text: Union[str, List[str]]) -> np.ndarray:
        """
        Convert text into dense embeddings using the Nomic embedding model.
        
        Args:
            text: Single text string or list of text strings
            
        Returns:
            np.ndarray: Dense vector representation(s) of the input text
        """
        try:
            if isinstance(text, str):
                text = [text]
            
            # Use sentence-transformers for easier handling
            embeddings = self.sentence_model.encode(text, normalize_embeddings=True)
            
            if len(text) == 1:
                return embeddings[0]
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise
    
    def get_embeddings_manual(self, text: Union[str, List[str]]) -> np.ndarray:
        """
        Manual embedding generation using transformers (alternative method)
        """
        try:
            if isinstance(text, str):
                text = [text]
            
            embeddings = []
            for t in text:
                # Tokenize and prepare input
                inputs = self.tokenizer(t, return_tensors="pt", padding=True, truncation=True)
                
                # Forward pass
                with torch.no_grad():
                    outputs = self.model(**inputs)
                
                # Mean pooling across token embeddings
                embedding = outputs.last_hidden_state.mean(dim=1)
                embeddings.append(embedding[0].numpy())
            
            embeddings = np.array(embeddings)
            
            if len(text) == 1:
                return embeddings[0]
            return embeddings
            
        except Exception as e:
            logger.error(f"Error in manual embedding generation: {e}")
            raise

# Global embedding service instance
embedding_service = None

def get_embedding_service() -> EmbeddingService:
    """Get global embedding service instance"""
    global embedding_service
    if embedding_service is None:
        embedding_service = EmbeddingService()
    return embedding_service