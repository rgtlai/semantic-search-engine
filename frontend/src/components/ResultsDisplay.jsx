import React, { useState } from 'react';

const ResultsDisplay = ({ 
  searchResponse, 
  logs = [], 
  cacheStats, 
  isLoading = false 
}) => {
  const [activeTab, setActiveTab] = useState('answer');

  const getQueryTypeColor = (queryType) => {
    switch (queryType) {
      case 'OPENAI_QUERY':
        return 'bg-blue-100 text-blue-800';
      case '10K_DOCUMENT_QUERY':
        return 'bg-green-100 text-green-800';
      case 'INTERNET_QUERY':
        return 'bg-purple-100 text-purple-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getLogLevelColor = (level) => {
    switch (level.toUpperCase()) {
      case 'ERROR':
        return 'text-red-600 bg-red-50';
      case 'WARNING':
        return 'text-yellow-600 bg-yellow-50';
      case 'INFO':
        return 'text-blue-600 bg-blue-50';
      case 'DEBUG':
        return 'text-gray-600 bg-gray-50';
      default:
        return 'text-gray-600 bg-gray-50';
    }
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  const tabs = [
    { id: 'answer', label: 'Answer', count: searchResponse ? 1 : 0 },
    { id: 'sources', label: 'Sources', count: searchResponse?.sources?.length || 0 },
    { id: 'logs', label: 'Logs', count: logs.length },
    { id: 'cache', label: 'Cache', count: cacheStats ? 1 : 0 }
  ];

  if (isLoading) {
    return (
      <div className="card">
        <div className="animate-pulse">
          <div className="flex space-x-1 mb-4">
            {tabs.map(tab => (
              <div key={tab.id} className="h-8 w-20 bg-gray-200 rounded"></div>
            ))}
          </div>
          <div className="space-y-3">
            <div className="h-4 bg-gray-200 rounded w-3/4"></div>
            <div className="h-4 bg-gray-200 rounded w-1/2"></div>
            <div className="h-4 bg-gray-200 rounded w-5/6"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      {/* Tab Navigation */}
      <div className="flex space-x-1 mb-6 border-b">
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`
              px-4 py-2 text-sm font-medium rounded-t-lg transition-colors duration-200
              ${activeTab === tab.id
                ? 'bg-primary-50 text-primary-700 border-b-2 border-primary-600'
                : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
              }
            `}
          >
            {tab.label}
            {tab.count > 0 && (
              <span className="ml-2 inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                {tab.count}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="min-h-[200px]">
        {activeTab === 'answer' && (
          <div className="space-y-4">
            {searchResponse ? (
              <>
                {/* Query Type Badge */}
                <div className="flex items-center space-x-2 mb-4">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getQueryTypeColor(searchResponse.query_type)}`}>
                    {searchResponse.query_type?.replace('_', ' ')}
                  </span>
                  {searchResponse.processing_time && (
                    <span className="text-xs text-gray-500">
                      {(searchResponse.processing_time * 1000).toFixed(0)}ms
                    </span>
                  )}
                </div>

                {/* Answer */}
                <div className="prose max-w-none">
                  <div className="whitespace-pre-wrap text-gray-800 leading-relaxed">
                    {searchResponse.answer}
                  </div>
                </div>

                {/* Cache Info */}
                {searchResponse.cache_metrics && (
                  <div className="mt-4 p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">Cache:</span>
                      <div className="flex items-center space-x-2">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                          searchResponse.cache_metrics.hit 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-yellow-100 text-yellow-800'
                        }`}>
                          {searchResponse.cache_metrics.hit ? 'HIT' : 'MISS'}
                        </span>
                        {searchResponse.cache_metrics.similarity_score && (
                          <span className="text-xs text-gray-500">
                            {(searchResponse.cache_metrics.similarity_score * 100).toFixed(1)}% similar
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                )}
              </>
            ) : (
              <div className="text-center text-gray-500 py-12">
                <svg className="mx-auto h-12 w-12 text-gray-300 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
                <p>No search results yet. Try asking a question!</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'sources' && (
          <div className="space-y-4">
            {searchResponse?.sources?.length > 0 ? (
              searchResponse.sources.map((source, index) => (
                <div key={index} className="border rounded-lg p-4 hover:bg-gray-50 transition-colors">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-900">
                      Source {index + 1}
                    </span>
                    <div className="flex items-center space-x-2">
                      <span className="px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                        {source.source_type}
                      </span>
                      {source.score && (
                        <span className="text-xs text-gray-500">
                          Score: {source.score.toFixed(3)}
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="text-sm text-gray-700 mb-2">
                    {source.content?.substring(0, 300)}
                    {source.content?.length > 300 && '...'}
                  </div>
                  {source.metadata && Object.keys(source.metadata).length > 0 && (
                    <details className="text-xs text-gray-500">
                      <summary className="cursor-pointer hover:text-gray-700">
                        View metadata
                      </summary>
                      <pre className="mt-2 p-2 bg-gray-100 rounded overflow-x-auto">
                        {JSON.stringify(source.metadata, null, 2)}
                      </pre>
                    </details>
                  )}
                </div>
              ))
            ) : (
              <div className="text-center text-gray-500 py-12">
                <svg className="mx-auto h-12 w-12 text-gray-300 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <p>No sources available</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'logs' && (
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {logs.length > 0 ? (
              logs.slice().reverse().map((log, index) => (
                <div key={log.id || index} className={`p-3 rounded-lg text-sm ${getLogLevelColor(log.data?.level || 'INFO')}`}>
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-medium text-xs">
                      {log.data?.component || 'System'}
                    </span>
                    <span className="text-xs opacity-75">
                      {formatTimestamp(log.timestamp)}
                    </span>
                  </div>
                  <div className="font-mono text-xs">
                    {log.data?.message || JSON.stringify(log.data)}
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center text-gray-500 py-12">
                <svg className="mx-auto h-12 w-12 text-gray-300 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
                <p>No logs available</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'cache' && (
          <div className="space-y-4">
            {cacheStats ? (
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-blue-50 p-4 rounded-lg">
                  <div className="text-2xl font-bold text-blue-800">
                    {cacheStats.cache_size || 0}
                  </div>
                  <div className="text-sm text-blue-600">Cache Entries</div>
                </div>
                <div className="bg-green-50 p-4 rounded-lg">
                  <div className="text-2xl font-bold text-green-800">
                    {(cacheStats.threshold * 100 || 80).toFixed(0)}%
                  </div>
                  <div className="text-sm text-green-600">Similarity Threshold</div>
                </div>
                <div className="bg-purple-50 p-4 rounded-lg">
                  <div className="text-2xl font-bold text-purple-800">
                    {cacheStats.embedding_dimension || 768}
                  </div>
                  <div className="text-sm text-purple-600">Embedding Dimensions</div>
                </div>
                <div className="bg-orange-50 p-4 rounded-lg">
                  <div className="text-xs font-mono text-orange-800 break-all">
                    {cacheStats.cache_file?.split('/').pop() || 'cache.json'}
                  </div>
                  <div className="text-sm text-orange-600">Cache File</div>
                </div>
              </div>
            ) : (
              <div className="text-center text-gray-500 py-12">
                <svg className="mx-auto h-12 w-12 text-gray-300 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                </svg>
                <p>No cache statistics available</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default ResultsDisplay;