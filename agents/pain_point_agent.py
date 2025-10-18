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
    
    def execute(self, product_or_domain: str, competitor_products: Optional[List[str]] = None, use_react: bool = False) -> Dict[str, Any]:
        """
        Mine pain points for a product or domain
        
        Args:
            product_or_domain: Product name or domain to analyze
            competitor_products: Optional list of competitor products to analyze
            use_react: If True, use ReAct (Reasoning + Acting) for dynamic search
            
        Returns:
            Dictionary with pain points, sources, and insights
        """
        if use_react:
            return self.execute_with_react(product_or_domain, competitor_products)
        
        # Original implementation (predefined searches)
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
    
    def execute_with_react(self, product_or_domain: str, competitor_products: Optional[List[str]] = None, max_iterations: int = 6) -> Dict[str, Any]:
        """
        Mine pain points using ReAct (Reasoning + Acting) loop for dynamic, adaptive search
        
        This enables the agent to:
        - Reason about what it has learned
        - Decide what to search for next dynamically
        - Follow evidence trails to deeper insights
        - Stop when sufficient high-quality data is gathered
        
        Args:
            product_or_domain: Product name or domain to analyze
            competitor_products: Optional list of competitor products to analyze
            max_iterations: Maximum number of reasoning-action cycles (default: 6)
            
        Returns:
            Dictionary with pain points, sources, reasoning traces, and insights
        """
        print(f"\n🔍 Mining customer pain points (ReAct Mode): {product_or_domain}")
        print(f"   Using dynamic reasoning-action loop (max {max_iterations} iterations)\n")
        
        # Initialize state
        all_pain_points = []
        search_history = []
        reasoning_traces = []
        
        for iteration in range(max_iterations):
            print(f"━━━ Iteration {iteration + 1}/{max_iterations} ━━━")
            
            # ============================================
            # STEP 1: THOUGHT (Reasoning)
            # ============================================
            thought_prompt = self._build_react_thought_prompt(
                product_or_domain, 
                all_pain_points, 
                search_history,
                iteration
            )
            
            thought_response = self._call_llm(
                prompt=thought_prompt,
                temperature=0.4,
                max_tokens=800
            )
            
            try:
                thought = self._parse_json_with_validation(thought_response)
            except:
                print(f"   ⚠️  Failed to parse thought, using fallback")
                thought = self._fallback_thought(iteration, len(all_pain_points))
            
            print(f"💭 Thought: {thought.get('reasoning', 'No reasoning provided')[:200]}...")
            print(f"   Confidence: {thought.get('confidence', 'unknown')}")
            print(f"   Should continue: {thought.get('should_continue', False)}")
            
            reasoning_traces.append({
                'iteration': iteration + 1,
                'thought': thought
            })
            
            # ============================================
            # TERMINATION CHECK
            # ============================================
            if not thought.get('should_continue', False):
                print(f"✅ Stopping: {thought.get('termination_reason', 'Goal achieved')}\n")
                break
            
            # ============================================
            # STEP 2: ACTION (Execute based on reasoning)
            # ============================================
            action = thought.get('action', {})
            action_type = action.get('type', 'search')
            
            if action_type == 'search':
                search_query = action.get('search_query', '')
                search_source = action.get('search_source', 'general')
                
                print(f"🎬 Action: Searching '{search_query}' (source: {search_source})")
                
                # Execute search
                results = self._targeted_search(search_query, search_source)
                
                # ============================================
                # STEP 3: OBSERVATION (Analyze results)
                # ============================================
                if results:
                    extracted = self._extract_pain_points(results, search_query)
                    new_pain_points = extracted.get('pain_points', [])
                    
                    print(f"👁️  Observation: Found {len(new_pain_points)} new pain points from {len(results)} results")
                    
                    if new_pain_points:
                        # Show preview of first pain point
                        first_pp = new_pain_points[0]
                        print(f"   Example: \"{first_pp.get('problem', 'N/A')[:100]}...\"")
                    
                    all_pain_points.extend(new_pain_points)
                    search_history.append({
                        'iteration': iteration + 1,
                        'query': search_query,
                        'source': search_source,
                        'results_count': len(results),
                        'pain_points_found': len(new_pain_points),
                        'expected_insight': action.get('expected_insight', '')
                    })
                else:
                    print(f"👁️  Observation: No results found for this query")
                    search_history.append({
                        'iteration': iteration + 1,
                        'query': search_query,
                        'source': search_source,
                        'results_count': 0,
                        'pain_points_found': 0
                    })
            
            elif action_type == 'stop':
                print(f"✅ Agent decided to stop: {action.get('reason', 'Sufficient data gathered')}\n")
                break
            
            print()  # Blank line between iterations
        
        # ============================================
        # FINAL SYNTHESIS
        # ============================================
        print(f"📊 Synthesis: Clustering and prioritizing {len(all_pain_points)} pain points...")
        
        if all_pain_points:
            clustered = self._cluster_and_prioritize(all_pain_points, product_or_domain)
        else:
            print("   ⚠️  No pain points found. Using general analysis as fallback.")
            clustered = self._generate_generic_pain_points(product_or_domain)
        
        result = {
            'product_or_domain': product_or_domain,
            'method': 'react',
            'total_pain_points': len(all_pain_points),
            'total_iterations': len(search_history),
            'clustered_pain_points': clustered.get('clusters', []),
            'top_pain_points': clustered.get('top_pain_points', []),
            'search_history': search_history,
            'reasoning_traces': reasoning_traces,
            'summary': clustered.get('summary', '')
        }
        
        print(f"\n✅ ReAct Mining Complete:")
        print(f"   - Iterations: {len(search_history)}")
        print(f"   - Pain points found: {len(all_pain_points)}")
        print(f"   - Clusters identified: {len(clustered.get('clusters', []))}")
        
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
    
    # ============================================
    # ReAct Helper Methods
    # ============================================
    
    def _build_react_thought_prompt(self, product_or_domain: str, pain_points: List[Dict], 
                                     search_history: List[Dict], iteration: int) -> str:
        """Build prompt for ReAct reasoning step"""
        
        # Format search history
        history_text = ""
        if search_history:
            history_text = "**Previous Searches:**\n"
            for h in search_history[-3:]:  # Last 3 searches
                history_text += f"- Iteration {h['iteration']}: \"{h['query']}\" ({h['source']})\n"
                history_text += f"  → Found {h['pain_points_found']} pain points from {h['results_count']} results\n"
        else:
            history_text = "**Previous Searches:** None (first iteration)\n"
        
        # Format current findings
        findings_text = ""
        if pain_points:
            findings_text = f"**Pain Points Found So Far:** {len(pain_points)} total\n"
            # Show sample of recent pain points
            if len(pain_points) > 0:
                findings_text += "**Recent Examples:**\n"
                for pp in pain_points[-3:]:  # Last 3 pain points
                    findings_text += f"- {pp.get('problem', 'Unknown')[:100]}\n"
        else:
            findings_text = "**Pain Points Found So Far:** 0 (need to start searching)\n"
        
        prompt = f"""You are mining customer pain points for: {product_or_domain}

**Iteration:** {iteration + 1} of 6 maximum

{history_text}

{findings_text}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**YOUR TASK:** Think strategically about what to do next.

**Consider:**
1. **Gaps:** What types of pain points are we missing?
2. **Depth:** Do we need more specific/quantified details on existing pain points?
3. **Sources:** Have we explored diverse sources (Reddit, G2, Twitter, news)?
4. **Quality:** Are the pain points actionable and well-documented?
5. **Convergence:** Are we seeing patterns that suggest we've found the key issues?
6. **Sufficiency:** Do we have 15-20 high-quality, diverse pain points?

**Stopping Criteria:**
✓ Stop if: 15+ high-quality pain points with good diversity
✓ Stop if: Last 2 searches yielded no new insights
✓ Stop if: Clear patterns identified across multiple sources
✓ Continue if: Major gaps in understanding, low diversity, or insufficient data

**Output your reasoning as JSON:**
{{
  "reasoning": "Your detailed thought process about current state and next steps (2-3 sentences)",
  "confidence": "high|medium|low - How confident are you in your current understanding?",
  "gaps": ["What specific information or pain point categories are missing?"],
  "should_continue": true/false,
  "termination_reason": "Why stopping (only if should_continue is false)",
  "action": {{
    "type": "search|stop",
    "search_query": "Specific, targeted search query (if type is 'search')",
    "search_source": "reddit|g2|twitter|news|general",
    "expected_insight": "What specific insight you expect to gain from this search"
  }}
}}

**Examples of Good Reasoning:**

Example 1 (Early iteration):
{{
  "reasoning": "We have no data yet. Need to start broad to understand main pain point categories.",
  "confidence": "low",
  "gaps": ["All pain point categories unknown"],
  "should_continue": true,
  "action": {{
    "type": "search",
    "search_query": "{product_or_domain} biggest problems complaints",
    "search_source": "reddit",
    "expected_insight": "Identify 3-5 main pain point themes"
  }}
}}

Example 2 (Middle iteration):
{{
  "reasoning": "Found 8 pain points about 'integration complexity' but they're vague. Need quantified impact data.",
  "confidence": "medium",
  "gaps": ["Cost/time impact of integration issues", "Specific integration pain points"],
  "should_continue": true,
  "action": {{
    "type": "search",
    "search_query": "{product_or_domain} integration time cost hours",
    "search_source": "g2",
    "expected_insight": "Quantify integration pain with specific hours/costs"
  }}
}}

Example 3 (Late iteration - stopping):
{{
  "reasoning": "Have 18 well-documented pain points across 4 major themes with quantified impacts. Clear patterns identified. Sufficient for synthesis.",
  "confidence": "high",
  "gaps": ["Minor: could explore niche use cases, but have core pain points covered"],
  "should_continue": false,
  "termination_reason": "Sufficient high-quality data across diverse sources. 18 pain points with clear patterns and quantified impacts."
}}

**Provide your reasoning now:**"""
        
        return prompt
    
    def _targeted_search(self, query: str, source: str = "general") -> List[Any]:
        """Execute a targeted search based on source preference"""
        if not self.search_engine:
            return []
        
        try:
            # Modify query based on source
            if source == "reddit":
                modified_query = f"{query} site:reddit.com"
            elif source == "g2":
                modified_query = f"{query} site:g2.com reviews"
            elif source == "twitter":
                modified_query = f"{query} site:twitter.com OR site:x.com"
            elif source == "news":
                modified_query = f"{query} news article"
            else:
                modified_query = query
            
            results = self.search_engine.search(modified_query, num_results=5)
            return results
            
        except Exception as e:
            print(f"   ⚠️  Search failed: {str(e)}")
            return []
    
    def _fallback_thought(self, iteration: int, pain_points_count: int) -> Dict[str, Any]:
        """Provide fallback thought if LLM response parsing fails"""
        if pain_points_count < 10:
            return {
                "reasoning": f"Continuing search to gather more pain points (currently have {pain_points_count})",
                "confidence": "medium",
                "gaps": ["Need more pain point data"],
                "should_continue": True,
                "action": {
                    "type": "search",
                    "search_query": "customer complaints problems",
                    "search_source": "general",
                    "expected_insight": "Find additional pain points"
                }
            }
        else:
            return {
                "reasoning": f"Have {pain_points_count} pain points, sufficient for analysis",
                "confidence": "medium",
                "gaps": [],
                "should_continue": False,
                "termination_reason": "Fallback termination after gathering sufficient data"
            }

