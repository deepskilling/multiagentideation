"""
Trend Analysis Agent - Identifies emerging trends and predicts future needs
"""
import json
from typing import List, Dict, Any, Optional
from agents.base_agent import BaseAgent
from core.web_search import get_search_engine
from config import config


class TrendAnalysisAgent(BaseAgent):
    """Agent responsible for identifying emerging trends and future-casting"""
    
    def __init__(self, use_web_search: bool = True):
        super().__init__(
            name="TrendAnalyzer",
            model=config.STRATEGIST_MODEL,
            role_description="""You are a strategic futurist and trend analyst who identifies weak signals, 
            emerging technologies, and market shifts. You excel at connecting dots between seemingly unrelated 
            trends to predict future needs and opportunities."""
        )
        self.use_web_search = use_web_search
        self.search_engine = get_search_engine() if use_web_search and config.SERPER_API_KEY else None
    
    def execute(self, domain: str, time_horizon: str = "2-3 years") -> Dict[str, Any]:
        """
        Analyze trends for a domain
        
        Args:
            domain: Domain or industry to analyze
            time_horizon: How far ahead to predict (e.g., "2-3 years", "5 years")
            
        Returns:
            Dictionary with trends, predictions, and feature opportunities
        """
        print(f"\n🔮 Analyzing trends for: {domain} ({time_horizon} horizon)")
        
        # Collect trends from multiple sources
        all_trends = []
        sources = []
        
        # Search for various types of trends
        search_queries = self._build_search_queries(domain)
        
        for query in search_queries:
            print(f"   Searching: {query}")
            results = self._search_for_trends(query)
            
            if results:
                # Extract trends from search results
                trends = self._extract_trends(results, query, domain)
                all_trends.extend(trends.get('trends', []))
                sources.append({
                    'query': query,
                    'num_results': len(results),
                    'trends_found': len(trends.get('trends', []))
                })
        
        # Analyze and synthesize trends
        if all_trends:
            analysis = self._analyze_and_synthesize(all_trends, domain, time_horizon)
        else:
            print("   ⚠️  No trends found from search. Using knowledge-based analysis.")
            analysis = self._generate_knowledge_based_trends(domain, time_horizon)
        
        result = {
            'domain': domain,
            'time_horizon': time_horizon,
            'total_trends': len(all_trends),
            'trend_categories': analysis.get('categories', []),
            'key_predictions': analysis.get('predictions', []),
            'feature_opportunities': analysis.get('feature_opportunities', []),
            'sources': sources,
            'summary': analysis.get('summary', '')
        }
        
        print(f"   ✅ Identified {len(analysis.get('categories', []))} trend categories")
        
        return result
    
    def _build_search_queries(self, domain: str) -> List[str]:
        """Build search queries to find trends"""
        queries = [
            f"emerging trends {domain} 2025",
            f"future of {domain} predictions",
            f"{domain} technology trends 2025",
            f"{domain} market trends 2024 2025",
            f"what's next for {domain} industry"
        ]
        
        return queries[:5]  # Limit to 5 searches
    
    def _search_for_trends(self, query: str) -> List[Any]:
        """Search for trends using web search"""
        if not self.search_engine:
            return []
        
        try:
            results = self.search_engine.search(query, num_results=5)
            return results
        except Exception as e:
            print(f"   ⚠️  Search failed for '{query}': {str(e)}")
            return []
    
    def _extract_trends(self, search_results: List[Any], query: str, domain: str) -> Dict[str, Any]:
        """Extract trends from search results using LLM"""
        # Format search results for LLM
        results_text = "\n\n".join([
            f"Source: {r.title}\n{r.snippet}\nURL: {r.link}"
            for r in search_results
        ])
        
        prompt = f"""Analyze the following search results for emerging trends and future predictions in {domain}.

Search Query: {query}

Search Results:
{results_text}

Extract all emerging trends, technologies, and future predictions mentioned. For each trend:
1. What is the trend?
2. Why is it important?
3. What's driving it?
4. Maturity level (emerging/growing/mainstream)
5. Expected timeline

Output as JSON:
{{
  "trends": [
    {{
      "trend": "Name/description of the trend",
      "category": "Technology/Market/Social/Regulatory",
      "importance": "Why this matters",
      "drivers": "What's causing this trend",
      "maturity": "emerging/growing/mainstream",
      "timeline": "When this will be important (e.g., '2025-2026')",
      "source_quote": "Direct quote if available"
    }}
  ]
}}

Focus on specific, actionable trends with clear implications.
"""
        
        try:
            response = self._call_llm(
                prompt=prompt,
                temperature=0.4,
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
            print(f"   ⚠️  Error extracting trends: {str(e)}")
            return {"trends": []}
    
    def _analyze_and_synthesize(self, trends: List[Dict[str, Any]], domain: str, 
                                time_horizon: str) -> Dict[str, Any]:
        """Analyze trends and generate predictions"""
        # Format trends for LLM
        trends_text = "\n\n".join([
            f"Trend: {t.get('trend', '')}\n"
            f"Category: {t.get('category', '')}\n"
            f"Importance: {t.get('importance', '')}\n"
            f"Drivers: {t.get('drivers', '')}\n"
            f"Maturity: {t.get('maturity', '')}\n"
            f"Timeline: {t.get('timeline', '')}"
            for t in trends
        ])
        
        prompt = f"""Analyze these trends for {domain} and predict future needs ({time_horizon} ahead).

Trends Identified:
{trends_text}

Tasks:
1. Categorize trends into themes
2. Identify convergence points (where trends intersect)
3. Make 5 specific predictions about future needs
4. Generate feature opportunities for each prediction

Output as JSON:
{{
  "categories": [
    {{
      "theme": "Category name (e.g., 'AI & Automation', 'Regulatory Shifts')",
      "trends": ["List of trends in this category"],
      "convergence": "How these trends interact/amplify each other",
      "impact_level": "high/medium/low"
    }}
  ],
  "predictions": [
    {{
      "rank": 1,
      "prediction": "Specific prediction about future need",
      "why": "Why this will happen",
      "timeline": "When (e.g., '2025', '2026-2027')",
      "confidence": "high/medium/low",
      "implications": "What this means for products"
    }}
  ],
  "feature_opportunities": [
    {{
      "feature": "Feature idea based on trends",
      "trend_basis": "Which trend(s) this leverages",
      "competitive_advantage": "Why this would be differentiated",
      "timing": "When to build this"
    }}
  ],
  "summary": "2-3 sentence synthesis of key insights"
}}
"""
        
        try:
            response = self._call_llm(
                prompt=prompt,
                temperature=0.5,
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
            print(f"   ⚠️  Error analyzing trends: {str(e)}")
            return {
                "categories": [],
                "predictions": [],
                "feature_opportunities": [],
                "summary": "Analysis failed"
            }
    
    def _generate_knowledge_based_trends(self, domain: str, time_horizon: str) -> Dict[str, Any]:
        """Generate trends based on LLM knowledge (fallback)"""
        prompt = f"""Based on your knowledge, what are the most important emerging trends in {domain} 
for the next {time_horizon}?

Provide:
1. Trend categories with specific trends
2. 5 predictions about future needs
3. Feature opportunities
4. Synthesis

Output as JSON:
{{
  "categories": [
    {{
      "theme": "Category name",
      "trends": ["List of trends"],
      "convergence": "How they interact",
      "impact_level": "high/medium/low"
    }}
  ],
  "predictions": [
    {{
      "rank": 1,
      "prediction": "Specific prediction",
      "why": "Reasoning",
      "timeline": "When",
      "confidence": "high/medium/low",
      "implications": "What it means"
    }}
  ],
  "feature_opportunities": [
    {{
      "feature": "Feature idea",
      "trend_basis": "Based on which trends",
      "competitive_advantage": "Why differentiated",
      "timing": "When to build"
    }}
  ],
  "summary": "Key insights"
}}
"""
        
        try:
            response = self._call_llm(prompt=prompt, temperature=0.6, max_tokens=3000)
            
            response = response.strip()
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
            
            return json.loads(response)
            
        except Exception as e:
            print(f"   ⚠️  Error generating knowledge-based trends: {str(e)}")
            return {
                "categories": [],
                "predictions": [],
                "feature_opportunities": [],
                "summary": "No trends available"
            }
    
    def format_for_generation(self, trend_analysis: Dict[str, Any]) -> str:
        """Format trend analysis for use in idea generation"""
        output = "**Trend Analysis & Future Predictions:**\n\n"
        
        # Add summary
        output += f"Summary: {trend_analysis.get('summary', '')}\n\n"
        
        # Add key predictions
        output += "**Key Predictions (Next 2-5 Years):**\n"
        for pred in trend_analysis.get('predictions', [])[:5]:
            output += f"{pred.get('rank')}. {pred.get('prediction', '')}\n"
            output += f"   Why: {pred.get('why', '')}\n"
            output += f"   Timeline: {pred.get('timeline', '')} (Confidence: {pred.get('confidence', '')})\n"
            output += f"   Implications: {pred.get('implications', '')}\n\n"
        
        # Add trend categories
        output += "**Trend Categories:**\n"
        for cat in trend_analysis.get('categories', [])[:3]:
            output += f"- {cat.get('theme', '')} ({cat.get('impact_level', '')} impact)\n"
            output += f"  Trends: {', '.join(cat.get('trends', [])[:3])}\n"
            output += f"  Convergence: {cat.get('convergence', '')}\n\n"
        
        # Add feature opportunities
        output += "**Feature Opportunities Based on Trends:**\n"
        for opp in trend_analysis.get('feature_opportunities', [])[:5]:
            output += f"- {opp.get('feature', '')}\n"
            output += f"  Trend Basis: {opp.get('trend_basis', '')}\n"
            output += f"  Advantage: {opp.get('competitive_advantage', '')}\n\n"
        
        return output.strip()

