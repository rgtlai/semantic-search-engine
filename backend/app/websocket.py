import json
import logging
import asyncio
from typing import Dict, Any
from fastapi import WebSocket, WebSocketDisconnect
from .models.query import SearchQuery
from .models.response import WebSocketMessage, LogMessage, ErrorResponse
from .services.rag_service import get_rag_service
from datetime import datetime

logger = logging.getLogger(__name__)

class ConnectionManager:
    """Manages WebSocket connections."""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        """Accept new WebSocket connection."""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"Client {client_id} connected")
    
    def disconnect(self, client_id: str):
        """Remove WebSocket connection."""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"Client {client_id} disconnected")
    
    async def send_message(self, client_id: str, message: Dict[str, Any]):
        """Send message to specific client."""
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_text(json.dumps(message, default=str))
            except Exception as e:
                logger.error(f"Error sending message to {client_id}: {e}")
                self.disconnect(client_id)
    
    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast message to all connected clients."""
        disconnected_clients = []
        for client_id, websocket in self.active_connections.items():
            try:
                await websocket.send_text(json.dumps(message, default=str))
            except Exception as e:
                logger.error(f"Error broadcasting to {client_id}: {e}")
                disconnected_clients.append(client_id)
        
        # Clean up disconnected clients
        for client_id in disconnected_clients:
            self.disconnect(client_id)

# Global connection manager
manager = ConnectionManager()

class WebSocketHandler:
    """Handles WebSocket communications for the search interface."""
    
    def __init__(self):
        self.rag_service = get_rag_service()
    
    async def handle_search_query(self, websocket: WebSocket, client_id: str, data: Dict[str, Any]):
        """Handle search query from WebSocket client."""
        try:
            # Parse search query
            search_query = SearchQuery(**data)
            
            # Send processing status
            await manager.send_message(client_id, {
                "type": "status",
                "data": {
                    "message": f"Processing query: {search_query.query}",
                    "status": "processing"
                },
                "timestamp": datetime.now().isoformat()
            })
            
            # Log the query
            await self._send_log(client_id, "INFO", f"Received query: {search_query.query}", "WebSocketHandler")
            
            # Process the query using RAG service
            if "sub_query" in data and data["sub_query"]:
                # Use sub-query processing
                response = self.rag_service.process_sub_queries(
                    search_query.query, 
                    search_query.allow_web_search
                )
            else:
                # Standard processing
                response = self.rag_service.process_query(
                    search_query.query, 
                    search_query.allow_web_search
                )
            
            # Send cache metrics if available
            if response.cache_metrics:
                cache_message = "Cache HIT" if response.cache_metrics.hit else "Cache MISS"
                if response.cache_metrics.hit:
                    cache_message += f" (similarity: {response.cache_metrics.similarity_score:.3f})"
                
                await self._send_log(client_id, "INFO", cache_message, "SemanticCache")
            
            # Send the response
            response_message = WebSocketMessage(
                type="search_response",
                data=response.dict()
            )
            
            await manager.send_message(client_id, response_message.dict())
            
            # Log completion
            await self._send_log(
                client_id, 
                "INFO", 
                f"Query completed in {response.processing_time:.2f}s", 
                "RAGService"
            )
            
        except Exception as e:
            logger.error(f"Error handling search query: {e}")
            
            error_response = ErrorResponse(
                error=str(e),
                error_type=type(e).__name__
            )
            
            error_message = WebSocketMessage(
                type="error",
                data=error_response.dict()
            )
            
            await manager.send_message(client_id, error_message.dict())
    
    async def handle_cache_stats(self, websocket: WebSocket, client_id: str):
        """Handle cache statistics request."""
        try:
            cache_stats = self.rag_service.cache_service.get_cache_stats()
            
            stats_message = WebSocketMessage(
                type="cache_stats",
                data=cache_stats
            )
            
            await manager.send_message(client_id, stats_message.dict())
            
        except Exception as e:
            logger.error(f"Error handling cache stats request: {e}")
            await self._send_error(client_id, str(e))
    
    async def _send_log(self, client_id: str, level: str, message: str, component: str):
        """Send log message to client."""
        log_message = LogMessage(
            level=level,
            message=message,
            component=component
        )
        
        ws_message = WebSocketMessage(
            type="log_message",
            data=log_message.dict()
        )
        
        await manager.send_message(client_id, ws_message.dict())
    
    async def _send_error(self, client_id: str, error_message: str):
        """Send error message to client."""
        error_response = ErrorResponse(
            error=error_message,
            error_type="WebSocketError"
        )
        
        error_msg = WebSocketMessage(
            type="error",
            data=error_response.dict()
        )
        
        await manager.send_message(client_id, error_msg.dict())

# Global WebSocket handler
ws_handler = WebSocketHandler()

async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """Main WebSocket endpoint handler."""
    await manager.connect(websocket, client_id)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            message_type = message.get("type")
            message_data = message.get("data", {})
            
            # Route message based on type
            if message_type == "search_query":
                await ws_handler.handle_search_query(websocket, client_id, message_data)
            elif message_type == "cache_stats":
                await ws_handler.handle_cache_stats(websocket, client_id)
            elif message_type == "ping":
                # Respond to ping with pong
                await manager.send_message(client_id, {
                    "type": "pong",
                    "data": {"timestamp": datetime.now().isoformat()}
                })
            else:
                await ws_handler._send_error(client_id, f"Unknown message type: {message_type}")
                
    except WebSocketDisconnect:
        manager.disconnect(client_id)
        logger.info(f"Client {client_id} disconnected")
    except Exception as e:
        logger.error(f"WebSocket error for client {client_id}: {e}")
        manager.disconnect(client_id)