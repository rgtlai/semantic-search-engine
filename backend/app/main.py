import logging
import os
from pathlib import Path
from fastapi import FastAPI, WebSocket, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from .utils.config import settings
from .models.query import SearchQuery
from .models.response import SearchResponse, HealthCheck, ErrorResponse
from .services.rag_service import get_rag_service
from .services.cache_service import get_cache_service
from .services.qdrant_service import get_qdrant_service
from .websocket import websocket_endpoint, manager

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Semantic Search Engine",
    description="RAG pipeline with multi-document retrieval, semantic caching, and agentic routing",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services on startup
@app.on_event("startup")
async def startup_event():
    """Initialize services when the application starts."""
    try:
        logger.info("Initializing services...")
        
        # Initialize RAG service (this will initialize all dependent services)
        rag_service = get_rag_service()
        logger.info("RAG service initialized")
        
        # Test Qdrant connection
        qdrant_service = get_qdrant_service()
        if qdrant_service.health_check():
            logger.info("Qdrant service is healthy")
        else:
            logger.warning("Qdrant service health check failed")
        
        # Initialize cache service
        cache_service = get_cache_service()
        cache_stats = cache_service.get_cache_stats()
        logger.info(f"Cache service initialized with {cache_stats['cache_size']} entries")
        
        logger.info("All services initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_route(websocket: WebSocket, client_id: str = Query(...)):
    """WebSocket endpoint for real-time search interface."""
    await websocket_endpoint(websocket, client_id)

# REST API endpoints
@app.get("/health", response_model=HealthCheck)
async def health_check():
    """Health check endpoint."""
    try:
        qdrant_healthy = get_qdrant_service().health_check()
        
        return HealthCheck(
            status="healthy" if qdrant_healthy else "degraded",
            components={
                "qdrant": qdrant_healthy,
                "cache": True,  # Cache service is always available
                "rag_pipeline": True
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthCheck(
            status="unhealthy",
            components={
                "qdrant": False,
                "cache": False,
                "rag_pipeline": False
            }
        )

@app.post("/api/search", response_model=SearchResponse)
async def search_api(query: SearchQuery):
    """Direct search API endpoint (alternative to WebSocket)."""
    try:
        rag_service = get_rag_service()
        
        # Process the query
        response = rag_service.process_query(
            query.query,
            query.allow_web_search
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error in search API: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing search query: {str(e)}"
        )

@app.post("/api/search/subquery", response_model=SearchResponse)
async def subquery_search_api(query: SearchQuery):
    """Sub-query division search API endpoint."""
    try:
        rag_service = get_rag_service()
        
        # Process with sub-query division
        response = rag_service.process_sub_queries(
            query.query,
            query.allow_web_search
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error in sub-query search API: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing sub-query search: {str(e)}"
        )

@app.get("/api/cache/stats")
async def get_cache_stats():
    """Get cache statistics."""
    try:
        cache_service = get_cache_service()
        stats = cache_service.get_cache_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting cache stats: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving cache stats: {str(e)}"
        )

@app.delete("/api/cache/clear")
async def clear_cache():
    """Clear the semantic cache."""
    try:
        cache_service = get_cache_service()
        cache_service.clear_cache()
        return {"message": "Cache cleared successfully"}
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error clearing cache: {str(e)}"
        )

# Serve React build files
@app.on_event("startup")
async def mount_static_files():
    """Mount static files after startup."""
    try:
        # Check if React build directory exists
        build_path = Path(settings.react_build_path)
        if build_path.exists() and build_path.is_dir():
            # Mount static files
            app.mount("/static", StaticFiles(directory=str(build_path / "static")), name="static")
            logger.info(f"Mounted static files from {build_path}")
            
            # Serve React app for all other routes
            @app.get("/{path:path}")
            async def serve_react_app(path: str):
                """Serve React app for frontend routes."""
                index_file = build_path / "index.html"
                if index_file.exists():
                    return FileResponse(str(index_file))
                else:
                    return HTMLResponse(
                        content="<h1>React build not found</h1><p>Please build the frontend first.</p>",
                        status_code=404
                    )
        else:
            logger.warning(f"React build directory not found at {build_path}")
            
            # Serve placeholder page
            @app.get("/")
            async def serve_placeholder():
                """Serve placeholder when React build is not available."""
                return HTMLResponse(
                    content="""
                    <html>
                        <head>
                            <title>Semantic Search Engine</title>
                            <style>
                                body { font-family: Arial, sans-serif; margin: 40px; }
                                .container { max-width: 800px; margin: 0 auto; }
                                .status { padding: 20px; background: #f0f0f0; border-radius: 5px; }
                                .endpoints { margin-top: 20px; }
                                .endpoint { margin: 10px 0; padding: 10px; background: #e8f4fd; border-radius: 3px; }
                            </style>
                        </head>
                        <body>
                            <div class="container">
                                <h1>Semantic Search Engine Backend</h1>
                                <div class="status">
                                    <p><strong>Status:</strong> Backend is running successfully!</p>
                                    <p><strong>React Frontend:</strong> Not built yet. Please run 'npm run build' in the frontend directory.</p>
                                </div>
                                
                                <div class="endpoints">
                                    <h2>Available Endpoints:</h2>
                                    <div class="endpoint">
                                        <strong>WebSocket:</strong> <code>ws://localhost:8000/ws?client_id=your_id</code>
                                    </div>
                                    <div class="endpoint">
                                        <strong>Search API:</strong> <code>POST /api/search</code>
                                    </div>
                                    <div class="endpoint">
                                        <strong>Sub-query Search:</strong> <code>POST /api/search/subquery</code>
                                    </div>
                                    <div class="endpoint">
                                        <strong>Health Check:</strong> <code>GET /health</code>
                                    </div>
                                    <div class="endpoint">
                                        <strong>Cache Stats:</strong> <code>GET /api/cache/stats</code>
                                    </div>
                                </div>
                                
                                <p><a href="/docs">View API Documentation</a></p>
                            </div>
                        </body>
                    </html>
                    """,
                    status_code=200
                )
                
    except Exception as e:
        logger.error(f"Error mounting static files: {e}")

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Custom 404 handler."""
    return HTMLResponse(
        content="<h1>404 Not Found</h1><p>The requested resource was not found.</p>",
        status_code=404
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Custom 500 handler."""
    logger.error(f"Internal server error: {exc}")
    return ErrorResponse(
        error="Internal server error",
        error_type="InternalServerError"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.fastapi_host,
        port=settings.fastapi_port,
        reload=True
    )