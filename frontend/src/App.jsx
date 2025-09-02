import React, { useState, useEffect, useCallback } from 'react';
import SearchInterface from './components/SearchInterface';
import ResultsDisplay from './components/ResultsDisplay';
import useWebSocket from './hooks/useWebSocket';
import { getWebSocketUrl, handleApiError } from './utils/api';

function App() {
  const [searchResponse, setSearchResponse] = useState(null);
  const [logs, setLogs] = useState([]);
  const [cacheStats, setCacheStats] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // Initialize WebSocket connection
  const wsUrl = getWebSocketUrl();
  const {
    isConnected,
    messages,
    sendSearchQuery,
    requestCacheStats,
    clearMessages,
    error: wsError
  } = useWebSocket(wsUrl);

  // Handle incoming WebSocket messages
  useEffect(() => {
    if (messages.length > 0) {
      const latestMessage = messages[messages.length - 1];
      
      switch (latestMessage.type) {
        case 'search_response':
          setSearchResponse(latestMessage.data);
          setIsLoading(false);
          break;
          
        case 'log_message':
          setLogs(prev => [...prev, latestMessage]);
          break;
          
        case 'cache_stats':
          setCacheStats(latestMessage.data);
          break;
          
        case 'status':
          if (latestMessage.data?.status === 'processing') {
            setIsLoading(true);
          }
          setLogs(prev => [...prev, latestMessage]);
          break;
          
        case 'error':
          setError(handleApiError(new Error(latestMessage.data?.error || 'Unknown error')));
          setIsLoading(false);
          break;
          
        default:
          console.log('Unhandled message type:', latestMessage.type, latestMessage.data);
      }
    }
  }, [messages]);

  // Handle WebSocket errors
  useEffect(() => {
    if (wsError) {
      setError(`Connection error: ${wsError}`);
      setIsLoading(false);
    }
  }, [wsError]);

  // Handle search submission
  const handleSearch = useCallback((searchParams) => {
    const { query, allowWebSearch, useSubQueryDivision } = searchParams;
    
    setError(null);
    setIsLoading(true);
    
    // Clear previous results but keep cache stats
    setSearchResponse(null);
    
    // Send search query via WebSocket
    const success = sendSearchQuery(query, allowWebSearch, useSubQueryDivision);
    
    if (!success) {
      setError('Failed to send search query. Please check your connection.');
      setIsLoading(false);
    }
  }, [sendSearchQuery]);

  // Handle cache stats request
  const handleRequestCacheStats = useCallback(() => {
    requestCacheStats();
  }, [requestCacheStats]);

  // Handle clear results
  const handleClearResults = useCallback(() => {
    setSearchResponse(null);
    setLogs([]);
    setError(null);
    clearMessages();
  }, [clearMessages]);

  // Auto-request cache stats on initial connection
  useEffect(() => {
    if (isConnected && !cacheStats) {
      setTimeout(() => {
        handleRequestCacheStats();
      }, 1000);
    }
  }, [isConnected, cacheStats, handleRequestCacheStats]);

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <div className="text-center">
            <h1 className="text-4xl font-bold text-gray-900 mb-2">
              Semantic Search Engine
            </h1>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Powered by RAG pipeline with multi-document retrieval, semantic caching, and agentic routing
            </p>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">Error</h3>
                <div className="mt-2 text-sm text-red-700">
                  {error}
                </div>
                <div className="mt-3">
                  <button
                    onClick={() => setError(null)}
                    className="text-sm bg-red-100 hover:bg-red-200 text-red-800 px-2 py-1 rounded transition-colors"
                  >
                    Dismiss
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-5 gap-8">
          {/* Left Column - Search Interface */}
          <div className="lg:col-span-2">
            <div className="sticky top-8">
              <SearchInterface
                onSearch={handleSearch}
                isLoading={isLoading}
                isConnected={isConnected}
                onClearResults={handleClearResults}
                onRequestCacheStats={handleRequestCacheStats}
              />
              
              {/* Connection Status Card */}
              <div className="mt-4 bg-white rounded-lg shadow-sm border border-gray-200 p-4">
                <h3 className="text-sm font-medium text-gray-700 mb-3">System Status</h3>
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">WebSocket</span>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      isConnected 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {isConnected ? 'Connected' : 'Disconnected'}
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Cache Entries</span>
                    <span className="text-gray-800 font-medium">
                      {cacheStats?.cache_size || '0'}
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Total Messages</span>
                    <span className="text-gray-800 font-medium">
                      {messages.length}
                    </span>
                  </div>
                </div>
              </div>

              {/* Quick Actions */}
              <div className="mt-4 bg-white rounded-lg shadow-sm border border-gray-200 p-4">
                <h3 className="text-sm font-medium text-gray-700 mb-3">Quick Actions</h3>
                <div className="space-y-2">
                  <button
                    onClick={handleRequestCacheStats}
                    disabled={!isConnected}
                    className="w-full text-left px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded transition-colors disabled:opacity-50"
                  >
                    Refresh Cache Stats
                  </button>
                  <button
                    onClick={handleClearResults}
                    className="w-full text-left px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded transition-colors"
                  >
                    Clear Results & Logs
                  </button>
                  <a
                    href="/docs"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="block w-full text-left px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded transition-colors"
                  >
                    View API Documentation
                  </a>
                </div>
              </div>
            </div>
          </div>

          {/* Right Column - Results */}
          <div className="lg:col-span-3">
            <ResultsDisplay
              searchResponse={searchResponse}
              logs={logs}
              cacheStats={cacheStats}
              isLoading={isLoading}
            />
          </div>
        </div>

        {/* Footer */}
        <footer className="mt-12 text-center text-sm text-gray-500">
          <p>
            Built with FastAPI, React, Qdrant, and OpenAI • 
            <a href="https://github.com" className="ml-1 text-primary-600 hover:text-primary-700">
              View Source
            </a>
          </p>
        </footer>
      </div>
    </div>
  );
}

export default App;