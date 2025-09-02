import { useState, useEffect, useRef, useCallback } from 'react';

const useWebSocket = (url) => {
  const [socket, setSocket] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [messages, setMessages] = useState([]);
  const [error, setError] = useState(null);
  const reconnectTimeoutRef = useRef(null);
  const maxReconnectAttempts = 5;
  const reconnectAttemptsRef = useRef(0);

  const connect = useCallback(() => {
    try {
      const clientId = `client_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      const wsUrl = `${url}?client_id=${clientId}`;
      
      console.log('Connecting to WebSocket:', wsUrl);
      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        console.log('WebSocket connected');
        setIsConnected(true);
        setError(null);
        reconnectAttemptsRef.current = 0;
      };

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          setMessages(prev => [...prev, {
            ...message,
            id: Date.now() + Math.random(),
            timestamp: new Date().toISOString()
          }]);
        } catch (err) {
          console.error('Error parsing WebSocket message:', err);
        }
      };

      ws.onclose = (event) => {
        console.log('WebSocket disconnected:', event.code, event.reason);
        setIsConnected(false);
        setSocket(null);

        // Attempt reconnection if not intentionally closed
        if (event.code !== 1000 && reconnectAttemptsRef.current < maxReconnectAttempts) {
          const delay = Math.pow(2, reconnectAttemptsRef.current) * 1000; // Exponential backoff
          console.log(`Reconnecting in ${delay}ms... (attempt ${reconnectAttemptsRef.current + 1}/${maxReconnectAttempts})`);
          
          reconnectTimeoutRef.current = setTimeout(() => {
            reconnectAttemptsRef.current++;
            connect();
          }, delay);
        } else if (reconnectAttemptsRef.current >= maxReconnectAttempts) {
          setError('Max reconnection attempts reached. Please refresh the page.');
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setError('WebSocket connection error');
      };

      setSocket(ws);
    } catch (err) {
      console.error('Error creating WebSocket:', err);
      setError('Failed to create WebSocket connection');
    }
  }, [url]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    if (socket) {
      socket.close(1000, 'Intentional disconnect');
      setSocket(null);
      setIsConnected(false);
    }
  }, [socket]);

  const sendMessage = useCallback((message) => {
    if (socket && isConnected) {
      try {
        socket.send(JSON.stringify(message));
        return true;
      } catch (err) {
        console.error('Error sending message:', err);
        setError('Failed to send message');
        return false;
      }
    } else {
      console.warn('WebSocket not connected, cannot send message');
      return false;
    }
  }, [socket, isConnected]);

  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  const sendSearchQuery = useCallback((query, allowWebSearch = true, useSubQuery = false) => {
    const message = {
      type: 'search_query',
      data: {
        query,
        allow_web_search: allowWebSearch,
        sub_query: useSubQuery
      }
    };
    
    return sendMessage(message);
  }, [sendMessage]);

  const requestCacheStats = useCallback(() => {
    const message = {
      type: 'cache_stats',
      data: {}
    };
    
    return sendMessage(message);
  }, [sendMessage]);

  const ping = useCallback(() => {
    const message = {
      type: 'ping',
      data: { timestamp: new Date().toISOString() }
    };
    
    return sendMessage(message);
  }, [sendMessage]);

  // Connect on mount
  useEffect(() => {
    connect();

    // Cleanup on unmount
    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  // Ping periodically to keep connection alive
  useEffect(() => {
    if (isConnected) {
      const pingInterval = setInterval(() => {
        ping();
      }, 30000); // Ping every 30 seconds

      return () => clearInterval(pingInterval);
    }
  }, [isConnected, ping]);

  return {
    socket,
    isConnected,
    messages,
    error,
    connect,
    disconnect,
    sendMessage,
    sendSearchQuery,
    requestCacheStats,
    clearMessages,
    ping
  };
};

export default useWebSocket;