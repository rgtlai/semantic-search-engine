import React, { useState, useRef, useEffect } from 'react';
import ToggleSwitch from './ToggleSwitch';

const SearchInterface = ({ 
  onSearch, 
  isLoading = false, 
  isConnected = false,
  onClearResults,
  onRequestCacheStats 
}) => {
  const [query, setQuery] = useState('');
  const [allowWebSearch, setAllowWebSearch] = useState(true);
  const [useSubQueryDivision, setUseSubQueryDivision] = useState(false);
  const textareaRef = useRef(null);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [query]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim() && !isLoading) {
      onSearch({
        query: query.trim(),
        allowWebSearch,
        useSubQueryDivision
      });
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleClear = () => {
    setQuery('');
    if (onClearResults) {
      onClearResults();
    }
  };

  const exampleQueries = [
    "What was Uber's revenue in 2021?",
    "How do I use OpenAI's chat completions API?",
    "What are the latest AI developments in 2024?",
    "Compare Lyft and Uber's financial performance and tell me about the latest travel tech trends"
  ];

  const handleExampleClick = (exampleQuery) => {
    setQuery(exampleQuery);
    if (textareaRef.current) {
      textareaRef.current.focus();
    }
  };

  return (
    <div className="card">
      {/* Connection Status */}
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold text-gray-900">Semantic Search Engine</h1>
        <div className="flex items-center space-x-2">
          <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-400' : 'bg-red-400'}`}></div>
          <span className="text-sm text-gray-600">
            {isConnected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
      </div>

      {/* Search Form */}
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="relative">
          <label htmlFor="query" className="block text-sm font-medium text-gray-700 mb-2">
            Ask a question
          </label>
          <textarea
            ref={textareaRef}
            id="query"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Enter your question here... (Press Enter to search, Shift+Enter for new line)"
            disabled={isLoading || !isConnected}
            className={`
              input-field resize-none min-h-[60px] max-h-40 overflow-y-auto
              ${isLoading || !isConnected ? 'opacity-50 cursor-not-allowed' : ''}
            `}
            rows="1"
          />
          {query && (
            <button
              type="button"
              onClick={handleClear}
              className="absolute top-8 right-3 text-gray-400 hover:text-gray-600 transition-colors"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          )}
        </div>

        {/* Settings */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 p-4 bg-gray-50 rounded-lg">
          <ToggleSwitch
            enabled={allowWebSearch}
            onChange={setAllowWebSearch}
            label="Allow Web Search"
            description="Enable internet search for external queries"
            disabled={isLoading}
          />
          <ToggleSwitch
            enabled={useSubQueryDivision}
            onChange={setUseSubQueryDivision}
            label="Sub-Query Division"
            description="Break complex queries into sub-questions"
            disabled={isLoading}
          />
        </div>

        {/* Action Buttons */}
        <div className="flex items-center justify-between">
          <div className="flex space-x-2">
            <button
              type="submit"
              disabled={!query.trim() || isLoading || !isConnected}
              className={`
                btn-primary flex items-center space-x-2
                ${(!query.trim() || isLoading || !isConnected) 
                  ? 'opacity-50 cursor-not-allowed' 
                  : 'hover:shadow-lg'
                }
              `}
            >
              {isLoading ? (
                <>
                  <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <span>Searching...</span>
                </>
              ) : (
                <>
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                  <span>Search</span>
                </>
              )}
            </button>

            {onRequestCacheStats && (
              <button
                type="button"
                onClick={onRequestCacheStats}
                disabled={isLoading || !isConnected}
                className="btn-secondary flex items-center space-x-2"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                </svg>
                <span>Cache Stats</span>
              </button>
            )}
          </div>

          <div className="text-xs text-gray-500">
            {query.length}/1000 characters
          </div>
        </div>
      </form>

      {/* Example Queries */}
      {!query && (
        <div className="mt-6">
          <h3 className="text-sm font-medium text-gray-700 mb-3">Try these examples:</h3>
          <div className="grid gap-2">
            {exampleQueries.map((example, index) => (
              <button
                key={index}
                onClick={() => handleExampleClick(example)}
                disabled={isLoading || !isConnected}
                className="text-left p-3 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-50 rounded-lg transition-colors border border-transparent hover:border-gray-200"
              >
                "{example}"
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default SearchInterface;