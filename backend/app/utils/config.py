from pydantic_settings import BaseSettings
from typing import List
import os
from pathlib import Path

class Settings(BaseSettings):
    # OpenAI Configuration
    openai_api_key: str
    
    # Qdrant Configuration
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str = ""
    
    # ARES API Configuration
    ares_api_key: str
    
    # Application Configuration
    fastapi_host: str = "localhost"
    fastapi_port: int = 8000
    react_build_path: str = "./frontend/build"
    log_level: str = "INFO"
    
    # Semantic Cache Configuration
    cache_similarity_threshold: float = 0.8
    faiss_index_type: str = "IndexFlatL2"
    embedding_dimension: int = 768
    cache_file_path: str = "./cache.json"
    
    # DuckDuckGo Search Configuration
    duckduckgo_enabled: bool = True
    max_search_results: int = 5
    
    # CORS Configuration
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()

# Ensure cache directory exists
cache_dir = Path(settings.cache_file_path).parent
cache_dir.mkdir(parents=True, exist_ok=True)