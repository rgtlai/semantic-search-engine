import requests
import logging
from typing import Dict, Any, Optional
from app.utils.config import settings

logger = logging.getLogger(__name__)

class WebSearchService:
    """
    Web search service using ARES API.
    Based on Module_1 implementation.
    """
    
    def __init__(self):
        self.ares_api_key = settings.ares_api_key
        self.ares_url = "https://api-ares.traversaal.ai/live/predict"
    
    def search_internet(self, query: str) -> Dict[str, Any]:
        """
        Fetch response from internet using ARES API.
        
        Args:
            query: User search query
            
        Returns:
            Dict containing response data
        """
        logger.info("Fetching response from internet 🌐")
        
        payload = {"query": [query]}
        headers = {
            "x-api-key": self.ares_api_key,
            "content-type": "application/json"
        }
        
        try:
            response = requests.post(self.ares_url, json=payload, headers=headers)
            response.raise_for_status()
            
            response_data = response.json()
            
            # Extract response text and structure the return data
            result = {
                "answer": response_data.get('data', {}).get('response_text', 'No response received.'),
                "source_type": "web_search",
                "full_response": response_data,
                "search_query": query
            }
            
            logger.info("Successfully fetched internet response")
            return result
            
        except requests.exceptions.HTTPError as http_err:
            error_msg = f"HTTP error occurred: {http_err}"
            logger.error(error_msg)
            return {
                "answer": error_msg,
                "source_type": "web_search_error",
                "error": str(http_err)
            }
            
        except requests.exceptions.RequestException as req_err:
            error_msg = f"Request error occurred: {req_err}"
            logger.error(error_msg)
            return {
                "answer": error_msg,
                "source_type": "web_search_error", 
                "error": str(req_err)
            }
            
        except Exception as err:
            error_msg = f"An unexpected error occurred: {err}"
            logger.error(error_msg)
            return {
                "answer": error_msg,
                "source_type": "web_search_error",
                "error": str(err)
            }

# DuckDuckGo search as backup (optional implementation)
class DuckDuckGoService:
    """
    DuckDuckGo search service (optional backup to ARES).
    """
    
    def __init__(self):
        self.enabled = settings.duckduckgo_enabled
        self.max_results = settings.max_search_results
    
    def search(self, query: str) -> Dict[str, Any]:
        """
        Placeholder for DuckDuckGo search implementation.
        """
        if not self.enabled:
            return {
                "answer": "DuckDuckGo search is disabled",
                "source_type": "duckduckgo_disabled"
            }
        
        # TODO: Implement DuckDuckGo search
        # For now, return placeholder
        return {
            "answer": f"DuckDuckGo search not yet implemented for query: {query}",
            "source_type": "duckduckgo_placeholder"
        }

# Global service instances
web_search_service = None
duckduckgo_service = None

def get_web_search_service() -> WebSearchService:
    """Get global web search service instance."""
    global web_search_service
    if web_search_service is None:
        web_search_service = WebSearchService()
    return web_search_service

def get_duckduckgo_service() -> DuckDuckGoService:
    """Get global DuckDuckGo service instance."""
    global duckduckgo_service
    if duckduckgo_service is None:
        duckduckgo_service = DuckDuckGoService()
    return duckduckgo_service