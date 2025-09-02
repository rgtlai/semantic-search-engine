// API utility functions for REST endpoints

const API_BASE_URL = process.env.REACT_APP_API_URL || '';

class ApiClient {
  constructor(baseURL = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`API request failed for ${endpoint}:`, error);
      throw error;
    }
  }

  async get(endpoint, params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const url = queryString ? `${endpoint}?${queryString}` : endpoint;
    
    return this.request(url, {
      method: 'GET',
    });
  }

  async post(endpoint, data = {}) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async delete(endpoint) {
    return this.request(endpoint, {
      method: 'DELETE',
    });
  }

  // Specific API methods

  async searchQuery(query, allowWebSearch = true) {
    return this.post('/api/search', {
      query,
      allow_web_search: allowWebSearch,
    });
  }

  async searchSubQuery(query, allowWebSearch = true) {
    return this.post('/api/search/subquery', {
      query,
      allow_web_search: allowWebSearch,
    });
  }

  async getHealthCheck() {
    return this.get('/health');
  }

  async getCacheStats() {
    return this.get('/api/cache/stats');
  }

  async clearCache() {
    return this.delete('/api/cache/clear');
  }
}

// Create and export a singleton instance
const apiClient = new ApiClient();

export default apiClient;

// Helper functions for common API operations
export const searchApi = {
  search: (query, allowWebSearch = true) => apiClient.searchQuery(query, allowWebSearch),
  searchSubQuery: (query, allowWebSearch = true) => apiClient.searchSubQuery(query, allowWebSearch),
};

export const cacheApi = {
  getStats: () => apiClient.getCacheStats(),
  clear: () => apiClient.clearCache(),
};

export const healthApi = {
  check: () => apiClient.getHealthCheck(),
};

// Utility function to determine WebSocket URL
export const getWebSocketUrl = () => {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  
  // In development, connect directly to backend
  if (process.env.NODE_ENV === 'development') {
    return `${protocol}//localhost:8000/ws`;
  }
  
  // In production, use the same host as frontend
  const host = window.location.host;
  return `${protocol}//${host}/ws`;
};

// Error handling utilities
export const handleApiError = (error) => {
  console.error('API Error:', error);
  
  if (error.message.includes('Failed to fetch')) {
    return 'Network error: Please check your connection and try again.';
  }
  
  if (error.message.includes('500')) {
    return 'Server error: Please try again later.';
  }
  
  return error.message || 'An unexpected error occurred.';
};