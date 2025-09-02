from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from .query import CacheMetrics, QueryType

class DocumentSource(BaseModel):
    content: str = Field(..., description="Document content/excerpt")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Document metadata")
    score: Optional[float] = Field(default=None, description="Relevance score")
    source_type: str = Field(..., description="Type of source (10k, openai, web)")

class SearchResponse(BaseModel):
    answer: str = Field(..., description="Generated answer")
    sources: List[DocumentSource] = Field(default_factory=list, description="Supporting documents")
    query_type: QueryType = Field(..., description="Type of query processed")
    cache_metrics: Optional[CacheMetrics] = Field(default=None, description="Cache performance metrics")
    processing_time: float = Field(..., description="Total processing time")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")

class LogMessage(BaseModel):
    level: str = Field(..., description="Log level (INFO, DEBUG, ERROR)")
    message: str = Field(..., description="Log message")
    timestamp: datetime = Field(default_factory=datetime.now, description="Log timestamp")
    component: str = Field(..., description="Component that generated the log")

class WebSocketMessage(BaseModel):
    type: str = Field(..., description="Message type (search_response, log_message, error)")
    data: Dict[str, Any] = Field(..., description="Message data")
    timestamp: datetime = Field(default_factory=datetime.now, description="Message timestamp")

class HealthCheck(BaseModel):
    status: str = Field(..., description="Service status")
    timestamp: datetime = Field(default_factory=datetime.now, description="Health check timestamp")
    components: Dict[str, bool] = Field(default_factory=dict, description="Component health status")

class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error message")
    error_type: str = Field(..., description="Type of error")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional error details")