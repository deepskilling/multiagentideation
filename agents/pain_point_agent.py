"""
Pain Point Mining Agent - Discovers customer pain points from reviews, forums, and feedback
"""
import json
from typing import List, Dict, Any, Optional
from agents.base_agent import BaseAgent
from core.web_search import get_search_engine
from config import config


class PainPointAgent(BaseAgent):
    """Agent responsible for mining customer pain points from various sources"""
    
    def __init__(self, use_web_search: bool = True):
        super().__init__(
            name="PainPointMiner",
            model=config.GENERATOR_MODEL,
            role_description="""You are an expert at analyzing customer feedback, reviews, and complaints 
            to identify deep, actionable pain points. You excel at reading between the lines to understand 
            what customers really need, even when they can't articulate it clearly."""
        )
        self.use_web_search = use_web_search
        self.search_engine = get_search_engine() if use_web_search and config.SERPER_API_KEY else None
    
    def execute(self, product_or_domain: str, competitor_products: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Mine pain points for a product or domain
        
        Args:
            product_or_domain: Product name or domain to analyze
            competitor_products: Optional list of competitor products to analyze
            
        Returns:
            Dictionary with pain points, sources, and insights
        """
        print(f"\n🔍 Mining customer pain points for: {product_or_domain}")
        
        # Collect pain points from multiple sources
        all_pain_points = []
        sources = []
        
        # Search for customer complaints and problems
        search_queries = self._build_search_queries(product_or_domain, competitor_products)
        
        for query in search_queries:
            print(f"   Searching: {query}")
            results = self._search_for_pain_points(query)
            
            if results:
                # Extract pain points from search results
                pain_points = self._extract_pain_points(results, query)
                all_pain_points.extend(pain_points.get('pain_points', []))
                sources.append({
                    'query': query,
                    'num_results': len(results),
                    'pain_points_found': len(pain_points.get('pain_points', []))
                })
        
        # Cluster and prioritize pain points
        if all_pain_points:
            clustered = self._cluster_and_prioritize(all_pain_points, product_or_domain)
        else:
            print("   ⚠️  No pain points found from search. Using general analysis.")
            clustered = self._generate_generic_pain_points(product_or_domain)
        
        result = {
            'product_or_domain': product_or_domain,
            'total_pain_points': len(all_pain_points),
            'clustered_pain_points': clustered.get('clusters', []),
            'top_pain_points': clustered.get('top_pain_points', []),
            'sources': sources,
            'summary': clustered.get('summary', '')
        }
        
        print(f"   ✅ Found {len(clustered.get('clusters', []))} pain point clusters")
        
        return result
    
    def _build_search_queries(self, product_or_domain: str, competitor_products: Optional[List[str]] = None) -> List[str]:
        """Build search queries to find pain points"""
        queries = [
            f"{product_or_domain} problems reddit",
            f"{product_or_domain} worst features",
            f"{product_or_domain} complaints",
            f"{product_or_domain} frustrating",
            f"{product_or_domain} wish list features"
        ]
        
        # Add competitor-specific queries
        if competitor_products:
            for competitor in competitor_products[:2]:  # Limit to avoid too many searches
                queries.append(f"{competitor} complaints reviews")
                queries.append(f"{competitor} vs alternatives why switch")
        
        return queries[:5]  # Limit to 5 searches to manage costs
    
    def _search_for_pain_points(self, query: str) -> List[Any]:
        """Search for pain points using web search"""
        if not self.search_engine:
            return []
        
        try:
            results = self.search_engine.search(query, num_results=5)
            return results
        except Exception as e:
            print(f"   ⚠️  Search failed for '{query}': {str(e)}")
            return []
    
    def _extract_pain_points(self, search_results: List[Any], query: str) -> Dict[str, Any]:
        """Extract pain points from search results using LLM"""
        # Format search results for LLM
        results_text = "\n\n".join([
            f"Source: {r.title}\n{r.snippet}\nURL: {r.link}"
            for r in search_results
        ])
        
        prompt = f"""Analyze the following search results for customer pain points and complaints.

Search Query: {query}

Search Results:
{results_text}

Extract all customer pain points, complaints, and frustrations mentioned. For each pain point:
1. What is the specific problem?
2. Why is it painful? (impact/consequence)
3. How frequently is it mentioned?
4. What solution do customers want?

Output as JSON:
{{
  "pain_points": [
    {{
      "problem": "Brief description of the problem",
      "impact": "Why it's painful / consequences",
      "frequency": "high/medium/low",
      "desired_solution": "What customers want instead",
      "quote": "Direct quote from search results if available"
    }}
  ]
}}

Focus on actionable, specific pain points. Ignore vague complaints.
"""
        
        try:
            response = self._call_llm(
                prompt=prompt,
                temperature=0.3,  # Low temperature for consistent extraction
                max_tokens=2000
            )
            
            # Parse JSON response
            response = response.strip()
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
            
            return json.loads(response)
            
        except Exception as e:
            print(f"   ⚠️  Error extracting pain points: {str(e)}")
            return {"pain_points": []}
    
    def _cluster_and_prioritize(self, pain_points: List[Dict[str, Any]], product_or_domain: str) -> Dict[str, Any]:
        """Cluster similar pain points and prioritize them"""
        # Format pain points for LLM
        pain_points_text = "\n\n".join([
            f"Problem: {pp.get('problem', '')}\n"
            f"Impact: {pp.get('impact', '')}\n"
            f"Frequency: {pp.get('frequency', '')}\n"
            f"Desired: {pp.get('desired_solution', '')}"
            for pp in pain_points
        ])
        
        prompt = f"""Analyze these customer pain points for {product_or_domain} and organize them.

Pain Points:
{pain_points_text}

Tasks:
1. Cluster similar pain points into themes
2. Prioritize by impact and frequency
3. Identify the top 5 most critical pain points
4. Provide actionable insights

Output as JSON:
{{
  "clusters": [
    {{
      "theme": "Theme name (e.g., 'Usability', 'Performance')",
      "pain_points": ["List of related problems"],
      "priority": "high/medium/low",
      "potential_features": ["Feature ideas to solve these"]
    }}
  ],
  "top_pain_points": [
    {{
      "rank": 1,
      "problem": "Most critical problem",
      "why_critical": "Why this is #1",
      "feature_opportunity": "Specific feature to solve it"
    }}
  ],
  "summary": "2-3 sentence summary of key insights"
}}
"""
        
        try:
            response = self._call_llm(
                prompt=prompt,
                temperature=0.4,
                max_tokens=3000
            )
            
            # Parse JSON response
            response = response.strip()
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
            
            return json.loads(response)
            
        except Exception as e:
            print(f"   ⚠️  Error clustering pain points: {str(e)}")
            return {
                "clusters": [],
                "top_pain_points": [],
                "summary": "Analysis failed"
            }
    
    def _generate_generic_pain_points(self, product_or_domain: str) -> Dict[str, Any]:
        """Generate generic pain points when search fails (fallback)"""
        prompt = f"""Based on your knowledge of {product_or_domain} industry, what are the most common 
customer pain points and frustrations?

Provide:
1. Top 5 pain point clusters
2. Prioritized list of critical problems
3. Feature opportunities

Output as JSON:
{{
  "clusters": [
    {{
      "theme": "Theme name",
      "pain_points": ["List of problems"],
      "priority": "high/medium/low",
      "potential_features": ["Feature ideas"]
    }}
  ],
  "top_pain_points": [
    {{
      "rank": 1,
      "problem": "Problem description",
      "why_critical": "Why this matters",
      "feature_opportunity": "Feature to solve it"
    }}
  ],
  "summary": "Summary of insights"
}}
"""
        
        try:
            response = self._call_llm(prompt=prompt, temperature=0.5, max_tokens=2000)
            
            response = response.strip()
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
            
            return json.loads(response)
            
        except Exception as e:
            print(f"   ⚠️  Error generating generic pain points: {str(e)}")
            return {
                "clusters": [],
                "top_pain_points": [],
                "summary": "No pain points available"
            }
    
    def format_for_generation(self, pain_point_analysis: Dict[str, Any]) -> str:
        """Format pain point analysis for use in idea generation"""
        output = "**Customer Pain Points Analysis:**\n\n"
        
        # Add summary
        output += f"Summary: {pain_point_analysis.get('summary', '')}\n\n"
        
        # Add top pain points
        output += "**Top Priority Pain Points:**\n"
        for pp in pain_point_analysis.get('top_pain_points', [])[:5]:
            output += f"{pp.get('rank')}. {pp.get('problem', '')}\n"
            output += f"   Why Critical: {pp.get('why_critical', '')}\n"
            output += f"   Opportunity: {pp.get('feature_opportunity', '')}\n\n"
        
        # Add clusters
        output += "**Pain Point Themes:**\n"
        for cluster in pain_point_analysis.get('clusters', [])[:3]:
            output += f"- {cluster.get('theme', '')} ({cluster.get('priority', '')} priority)\n"
            output += f"  Problems: {', '.join(cluster.get('pain_points', [])[:3])}\n"
            output += f"  Features: {', '.join(cluster.get('potential_features', [])[:2])}\n\n"
        
        return output.strip()

