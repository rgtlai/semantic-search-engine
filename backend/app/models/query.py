from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum

class QueryType(str, Enum):
    OPENAI_QUERY = "OPENAI_QUERY"
    DOCUMENT_10K_QUERY = "10K_DOCUMENT_QUERY"
    INTERNET_QUERY = "INTERNET_QUERY"

class SearchQuery(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000, description="User search query")
    allow_web_search: bool = Field(default=True, description="Whether to allow web search")
    session_id: Optional[str] = Field(default=None, description="Session identifier")

class RouterResponse(BaseModel):
    action: QueryType = Field(..., description="Determined query type")
    reason: str = Field(..., description="Reasoning for the routing decision")
    answer: Optional[str] = Field(default="", description="Quick answer if available")
    confidence: Optional[float] = Field(default=None, description="Confidence score")

class CacheMetrics(BaseModel):
    hit: bool = Field(..., description="Whether query resulted in cache hit")
    similarity_score: Optional[float] = Field(default=None, description="Similarity score for cache hit")
    response_time: float = Field(..., description="Response time in seconds")
    cache_size: int = Field(..., description="Current cache size")

class SubQuery(BaseModel):
    query: str = Field(..., description="Individual sub-query")
    query_type: Optional[QueryType] = Field(default=None, description="Type of sub-query")

class SubQueryResponse(BaseModel):
    subQuestions: List[str] = Field(..., description="List of divided sub-questions")