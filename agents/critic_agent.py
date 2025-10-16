"""
Critic Agent - Evaluates SaaS ideas on multiple dimensions
"""
import json
from typing import List
from agents.base_agent import BaseAgent
from core.models import SaaSIdea, Evaluation
from config import config


class CriticAgent(BaseAgent):
    """Agent responsible for evaluating and scoring SaaS ideas"""
    
    def __init__(self):
        super().__init__(
            name="Critic",
            model=config.CRITIC_MODEL,
            role_description="You are an expert product evaluator and venture analyst. Your role is to critically assess SaaS ideas on novelty, feasibility, market fit, and business viability."
        )
    
    def execute(self, ideas: List[SaaSIdea]) -> List[Evaluation]:
        """
        Evaluate a list of SaaS ideas
        
        Args:
            ideas: List of SaaSIdea objects to evaluate
            
        Returns:
            List of Evaluation objects
        """
        evaluations = []
        
        for idea in ideas:
            self.log_message(f"Evaluating idea: {idea.idea_name}")
            evaluation = self._evaluate_single_idea(idea)
            evaluations.append(evaluation)
        
        return evaluations
    
    def _evaluate_single_idea(self, idea: SaaSIdea) -> Evaluation:
        """Evaluate a single idea"""
        prompt = self._build_evaluation_prompt(idea)
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
    
    def _build_evaluation_prompt(self, idea: SaaSIdea) -> str:
        """Build prompt for evaluating an idea"""
        prompt = f"""Evaluate the following SaaS product idea on four dimensions:

**Product Idea:**
- Name: {idea.idea_name}
- Problem: {idea.problem_statement}
- Target User: {idea.target_user}
- Core Features: {', '.join(idea.core_features)}
- Differentiator: {idea.differentiator}
- Tech Stack: {', '.join(idea.tech_stack)}
- Revenue Model: {idea.revenue_model}
- Domain: {idea.domain}

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

