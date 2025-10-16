"""
Critic Agent - Evaluates SaaS ideas on multiple dimensions
"""
import json
from typing import List, Optional
from agents.base_agent import BaseAgent
from core.models import SaaSIdea, Evaluation
from core.web_search import get_search_engine
from config import config


class CriticAgent(BaseAgent):
    """Agent responsible for evaluating and scoring SaaS ideas"""
    
    def __init__(self, use_web_search: bool = False):
        super().__init__(
            name="Critic",
            model=config.CRITIC_MODEL,
            role_description="You are an expert product evaluator and venture analyst. Your role is to critically assess SaaS ideas on novelty, feasibility, market fit, and business viability."
        )
        self.use_web_search = use_web_search
        self.search_engine = get_search_engine() if use_web_search and config.SERPER_API_KEY else None
    
    def execute(self, ideas: List[SaaSIdea], use_search: Optional[bool] = None) -> List[Evaluation]:
        """
        Evaluate a list of SaaS ideas
        
        Args:
            ideas: List of SaaSIdea objects to evaluate
            use_search: Override the instance's use_web_search setting
            
        Returns:
            List of Evaluation objects
        """
        # Allow per-call override of web search
        search_enabled = use_search if use_search is not None else self.use_web_search
        
        evaluations = []
        
        for idea in ideas:
            self.log_message(f"Evaluating idea: {idea.idea_name}")
            evaluation = self._evaluate_single_idea(idea, search_enabled)
            evaluations.append(evaluation)
        
        return evaluations
    
    def _evaluate_single_idea(self, idea: SaaSIdea, use_search: bool = False) -> Evaluation:
        """Evaluate a single idea"""
        
        # Perform web search if enabled
        search_context = ""
        if use_search and self.search_engine:
            search_context = self._get_search_context(idea)
        
        prompt = self._build_evaluation_prompt(idea, search_context)
        system_message = self._build_system_message()
        
        response = self._call_llm(
            prompt=prompt,
            system_message=system_message,
            temperature=0.3,  # Lower temperature for consistent evaluation
            max_tokens=2000
        )
        
        # Parse the evaluation response
        evaluation = self._parse_evaluation(response, idea)
        
        # Calculate composite score
        evaluation.calculate_composite_score(
            novelty_weight=config.NOVELTY_WEIGHT,
            feasibility_weight=config.FEASIBILITY_WEIGHT,
            market_fit_weight=config.MARKET_FIT_WEIGHT,
            viability_weight=config.VIABILITY_WEIGHT
        )
        
        self.log_message(f"Evaluated {idea.idea_name}: Score = {evaluation.composite_score:.3f}")
        return evaluation
    
    def _build_system_message(self) -> str:
        """Build system message for evaluation"""
        return """You are a senior product strategist and venture analyst with expertise in:
- Evaluating SaaS product ideas
- Market analysis and competitive assessment
- Technical feasibility evaluation
- Business model viability
- Innovation and differentiation analysis

Your evaluations are:
- Objective and data-driven
- Balanced between optimism and realism
- Specific with concrete justifications
- Focused on both strengths and weaknesses"""
    
    def _get_search_context(self, idea: SaaSIdea) -> str:
        """Get web search context for an idea"""
        print(f"      🔍 Searching web for: {idea.idea_name}")
        
        search_results = []
        
        try:
            # Search for competitors
            competitors = self.search_engine.search_competitors(
                domain=idea.domain,
                product_type="SaaS",
                num_results=3
            )
            
            # Search for market trends
            market_trends = self.search_engine.search_market_trends(
                domain=idea.domain,
                topic=idea.idea_name,
                num_results=2
            )
            
            search_results = competitors + market_trends
            
            if search_results:
                context = self.search_engine.format_results_for_prompt(search_results, max_length=800)
                print(f"      ✅ Found {len(search_results)} relevant results")
                return context
            else:
                print(f"      ⚠️  No search results found")
                return ""
                
        except Exception as e:
            print(f"      ⚠️  Search failed: {str(e)}")
            return ""
    
    def _build_evaluation_prompt(self, idea: SaaSIdea, search_context: str = "") -> str:
        """Build prompt for evaluating an idea"""
        
        # Add search context if available
        search_section = ""
        if search_context:
            search_section = f"\n\n**Market Intelligence (from web search):**\n{search_context}\n\nUse this real-time market data to inform your evaluation, especially for novelty and market fit assessments."
        
        prompt = f"""Evaluate the following SaaS product idea on four dimensions:

**Product Idea:**
- Name: {idea.idea_name}
- Problem: {idea.problem_statement}
- Target User: {idea.target_user}
- Core Features: {', '.join(idea.core_features)}
- Differentiator: {idea.differentiator}
- Tech Stack: {', '.join(idea.tech_stack)}
- Revenue Model: {idea.revenue_model}
- Domain: {idea.domain}{search_section}

**Evaluation Criteria:**

1. **Novelty (0.0 - 1.0)**: How innovative and unique is this idea?
   - 0.0-0.3: Copycat or very common
   - 0.4-0.6: Some novel aspects
   - 0.7-0.9: Highly innovative
   - 1.0: Groundbreaking

2. **Feasibility (0.0 - 1.0)**: How realistic is this to build and deploy?
   - Consider technical complexity, resource requirements, time to market
   - 0.0-0.3: Very difficult or impractical
   - 0.4-0.6: Moderate challenges
   - 0.7-0.9: Realistic and achievable
   - 1.0: Straightforward implementation

3. **Market Fit (0.0 - 1.0)**: How well does this address a real market need?
   - Consider problem significance, target user clarity, market size
   - 0.0-0.3: Unclear or weak market need
   - 0.4-0.6: Moderate market opportunity
   - 0.7-0.9: Strong market demand
   - 1.0: Critical, urgent market need

4. **Viability (0.0 - 1.0)**: How viable is this as a sustainable business?
   - Consider revenue potential, competition, scalability, ROI
   - 0.0-0.3: Weak business case
   - 0.4-0.6: Moderate business potential
   - 0.7-0.9: Strong business model
   - 1.0: Exceptional business opportunity

**Output Format (JSON):**
{{
  "novelty": 0.X,
  "feasibility": 0.X,
  "market_fit": 0.X,
  "viability": 0.X,
  "justification": "Detailed explanation covering all four dimensions, including strengths and weaknesses"
}}

Provide your evaluation now:"""
        
        return prompt
    
    def _parse_evaluation(self, response: str, idea: SaaSIdea) -> Evaluation:
        """Parse evaluation response into Evaluation object"""
        try:
            # Extract JSON from response
            response = response.strip()
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
            
            eval_data = json.loads(response)
            
            evaluation = Evaluation(
                idea_id=idea.idea_id,
                novelty=float(eval_data["novelty"]),
                feasibility=float(eval_data["feasibility"]),
                market_fit=float(eval_data["market_fit"]),
                viability=float(eval_data["viability"]),
                justification=eval_data["justification"],
                evaluated_by=self.name
            )
            
            return evaluation
            
        except Exception as e:
            self.log_message(f"Error parsing evaluation: {e}")
            # Return default mid-range scores if parsing fails
            return Evaluation(
                idea_id=idea.idea_id,
                novelty=0.5,
                feasibility=0.5,
                market_fit=0.5,
                viability=0.5,
                justification=f"Evaluation parsing failed: {str(e)}. Default scores applied.",
                evaluated_by=self.name
            )
    
    def batch_evaluate(self, ideas: List[SaaSIdea], batch_size: int = 5) -> List[Evaluation]:
        """
        Evaluate ideas in batches for efficiency
        
        Args:
            ideas: List of ideas to evaluate
            batch_size: Number of ideas to evaluate in one prompt
            
        Returns:
            List of evaluations
        """
        all_evaluations = []
        
        for i in range(0, len(ideas), batch_size):
            batch = ideas[i:i + batch_size]
            evaluations = self.execute(batch)
            all_evaluations.extend(evaluations)
        
        return all_evaluations

