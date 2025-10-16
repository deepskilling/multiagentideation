"""
Web Search Engine using Serper API for real-time market intelligence
"""
import requests
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from config import config


class SearchResult:
    """Represents a single search result"""
    
    def __init__(self, title: str, snippet: str, link: str, position: int = 0):
        self.title = title
        self.snippet = snippet
        self.link = link
        self.position = position
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'title': self.title,
            'snippet': self.snippet,
            'link': self.link,
            'position': self.position
        }
    
    def __str__(self) -> str:
        return f"{self.title}\n{self.snippet}\n{self.link}"


class WebSearchEngine:
    """Web search engine using Serper API"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize web search engine
        
        Args:
            api_key: Serper API key (defaults to config.SERPER_API_KEY)
        """
        self.api_key = api_key or config.SERPER_API_KEY
        self.base_url = "https://google.serper.dev/search"
        self.search_history: List[Dict[str, Any]] = []
        
        if not self.api_key:
            raise ValueError("SERPER_API_KEY not found. Please set it in your .env file")
    
    def search(self, query: str, num_results: int = 5) -> List[SearchResult]:
        """
        Perform a web search
        
        Args:
            query: Search query
            num_results: Number of results to return (max 10)
            
        Returns:
            List of SearchResult objects
        """
        headers = {
            'X-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        }
        
        payload = {
            'q': query,
            'num': min(num_results, 10)  # Serper API limit
        }
        
        try:
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Extract organic results
            organic_results = data.get('organic', [])
            
            # Convert to SearchResult objects
            results = []
            for i, result in enumerate(organic_results[:num_results]):
                search_result = SearchResult(
                    title=result.get('title', ''),
                    snippet=result.get('snippet', ''),
                    link=result.get('link', ''),
                    position=i + 1
                )
                results.append(search_result)
            
            # Record search history
            self.search_history.append({
                'timestamp': datetime.utcnow().isoformat(),
                'query': query,
                'num_results': len(results)
            })
            
            return results
            
        except requests.exceptions.RequestException as e:
            print(f"⚠️  Web search failed: {str(e)}")
            return []
        except Exception as e:
            print(f"⚠️  Unexpected error during search: {str(e)}")
            return []
    
    def search_competitors(self, domain: str, product_type: str, num_results: int = 5) -> List[SearchResult]:
        """
        Search for competitors in a specific domain
        
        Args:
            domain: Domain/industry (e.g., "GRC", "Healthcare")
            product_type: Type of product (e.g., "SaaS", "CRM")
            num_results: Number of results
            
        Returns:
            List of SearchResult objects
        """
        query = f"{product_type} competitors in {domain} industry 2024"
        return self.search(query, num_results)
    
    def search_market_trends(self, domain: str, topic: str, num_results: int = 5) -> List[SearchResult]:
        """
        Search for market trends
        
        Args:
            domain: Domain/industry
            topic: Specific topic
            num_results: Number of results
            
        Returns:
            List of SearchResult objects
        """
        query = f"{topic} trends in {domain} 2024 market analysis"
        return self.search(query, num_results)
    
    def search_pricing(self, product_name: str, domain: str, num_results: int = 3) -> List[SearchResult]:
        """
        Search for pricing information
        
        Args:
            product_name: Product or service name
            domain: Domain/industry
            num_results: Number of results
            
        Returns:
            List of SearchResult objects
        """
        query = f"{product_name} {domain} pricing plans 2024"
        return self.search(query, num_results)
    
    def search_customer_reviews(self, product_name: str, num_results: int = 3) -> List[SearchResult]:
        """
        Search for customer reviews and feedback
        
        Args:
            product_name: Product name
            num_results: Number of results
            
        Returns:
            List of SearchResult objects
        """
        query = f"{product_name} customer reviews feedback complaints"
        return self.search(query, num_results)
    
    def search_regulations(self, domain: str, topic: str, num_results: int = 3) -> List[SearchResult]:
        """
        Search for regulatory information
        
        Args:
            domain: Domain/industry
            topic: Regulatory topic
            num_results: Number of results
            
        Returns:
            List of SearchResult objects
        """
        query = f"{domain} {topic} regulations compliance requirements 2024"
        return self.search(query, num_results)
    
    def format_results_for_prompt(self, results: List[SearchResult], max_length: int = 1000) -> str:
        """
        Format search results for inclusion in LLM prompt
        
        Args:
            results: List of search results
            max_length: Maximum length of formatted string
            
        Returns:
            Formatted string
        """
        if not results:
            return "No search results available."
        
        formatted = "**Web Search Results:**\n\n"
        
        for result in results:
            entry = f"• **{result.title}**\n  {result.snippet}\n  Source: {result.link}\n\n"
            if len(formatted) + len(entry) > max_length:
                formatted += "...(more results truncated)"
                break
            formatted += entry
        
        return formatted.strip()
    
    def get_search_summary(self, results: List[SearchResult]) -> Dict[str, Any]:
        """
        Get a summary of search results
        
        Args:
            results: List of search results
            
        Returns:
            Summary dictionary
        """
        return {
            'total_results': len(results),
            'titles': [r.title for r in results],
            'sources': [r.link for r in results],
            'snippets': [r.snippet for r in results]
        }
    
    def get_search_history(self) -> List[Dict[str, Any]]:
        """Get search history"""
        return self.search_history
    
    def clear_history(self):
        """Clear search history"""
        self.search_history = []


# Global search engine instance
_search_engine = None


def get_search_engine() -> WebSearchEngine:
    """Get global search engine instance (singleton)"""
    global _search_engine
    if _search_engine is None:
        _search_engine = WebSearchEngine()
    return _search_engine

