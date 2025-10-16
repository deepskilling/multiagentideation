"""
Strategist Agent - Oversees the creative process and decides when to continue or stop
"""
import json
from typing import List, Dict, Any
from agents.base_agent import BaseAgent
from core.models import SaaSIdea, Evaluation, IterationResult
from config import config


class StrategistAgent(BaseAgent):
    """Agent responsible for strategic oversight and convergence detection"""
    
    def __init__(self):
        super().__init__(
            name="Strategist",
            model=config.STRATEGIST_MODEL,
            role_description="You are a strategic product leader. Your role is to assess the overall ideation process, monitor quality and diversity, and decide when to continue or stop iterations."
        )
        self.iteration_history = []
    
    def execute(self, iteration_result: IterationResult) -> Dict[str, Any]:
        """
        Assess an iteration and decide next steps
        
        Args:
            iteration_result: Results from the current iteration
            
        Returns:
            Dictionary with assessment and recommendations
        """
        self.iteration_history.append(iteration_result)
        
        assessment = self._assess_iteration(iteration_result)
        
        self.log_message(f"Iteration {iteration_result.iteration_number} assessment complete")
        return assessment
    
    def _assess_iteration(self, result: IterationResult) -> Dict[str, Any]:
        """Assess the iteration results"""
        
        # Calculate metrics
        avg_score = sum(e.composite_score for e in result.evaluations) / len(result.evaluations) if result.evaluations else 0.0
        max_score = max(e.composite_score for e in result.evaluations) if result.evaluations else 0.0
        
        # Build assessment prompt
        prompt = self._build_assessment_prompt(result, avg_score, max_score)
        
        response = self._call_llm(
            prompt=prompt,
            system_message=self.role_description,
            temperature=0.5,
            max_tokens=1500
        )
        
        # Parse assessment
        assessment = self._parse_assessment(response, result)
        
        return assessment
    
    def _build_assessment_prompt(self, result: IterationResult, avg_score: float, max_score: float) -> str:
        """Build prompt for iteration assessment"""
        
        # Summarize ideas
        ideas_summary = ""
        for i, idea in enumerate(result.generated_ideas[:5], 1):
            ideas_summary += f"\n{i}. {idea.idea_name}: {idea.problem_statement[:100]}..."
        
        # Historical context
        history_summary = ""
        if len(self.iteration_history) > 1:
            prev_scores = [
                max(e.composite_score for e in ir.evaluations) if ir.evaluations else 0.0
                for ir in self.iteration_history[:-1]
            ]
            history_summary = f"\nPrevious best scores: {[f'{s:.3f}' for s in prev_scores[-3:]]}"
        
        prompt = f"""Assess the current iteration of the SaaS ideation process:

**Iteration {result.iteration_number}**
- Ideas Generated: {len(result.generated_ideas)}
- Average Score: {avg_score:.3f}
- Best Score: {max_score:.3f}
{history_summary}

**Sample Ideas:**{ideas_summary}

**Your Assessment Should Consider:**
1. **Quality**: Are the scores improving? Is the best idea good enough?
2. **Diversity**: Are ideas sufficiently different from each other?
3. **Convergence**: Are we seeing diminishing returns?
4. **Feasibility**: Are the ideas practical and buildable?

**Decision Criteria:**
- Continue if: Scores are improving, high diversity, room for innovation
- Stop if: Scores plateaued, low diversity, found excellent ideas (score > 0.8)
- Max iterations: {config.MAX_ITERATIONS}

Output as JSON:
{{
  "should_continue": true/false,
  "confidence": 0.0-1.0,
  "reasoning": "Detailed explanation of decision",
  "recommendations": "What to focus on next (if continuing) or summary of best ideas (if stopping)",
  "quality_score": 0.0-1.0,
  "diversity_score": 0.0-1.0
}}

Your assessment:"""
        
        return prompt
    
    def _parse_assessment(self, response: str, result: IterationResult) -> Dict[str, Any]:
        """Parse assessment response"""
        try:
            response = response.strip()
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
            
            assessment_data = json.loads(response)
            
            # Override if max iterations reached
            if result.iteration_number >= config.MAX_ITERATIONS:
                assessment_data["should_continue"] = False
                assessment_data["reasoning"] += f" Max iterations ({config.MAX_ITERATIONS}) reached."
            
            return assessment_data
            
        except Exception as e:
            self.log_message(f"Error parsing assessment: {e}")
            # Default to continuing with caution
            return {
                "should_continue": result.iteration_number < config.MAX_ITERATIONS,
                "confidence": 0.5,
                "reasoning": f"Assessment parsing failed: {str(e)}",
                "recommendations": "Continue with caution",
                "quality_score": 0.5,
                "diversity_score": 0.5
            }
    
    def has_converged(self) -> bool:
        """Check if the creative process has converged"""
        if len(self.iteration_history) < 2:
            return False
        
        # Get last 3 iterations
        recent = self.iteration_history[-3:]
        
        # Check if scores have plateaued
        best_scores = [
            max(ir.evaluations, key=lambda e: e.composite_score).composite_score
            if ir.evaluations else 0.0
            for ir in recent
        ]
        
        # If improvement is less than 5% over last 3 iterations, consider converged
        if len(best_scores) >= 3:
            improvement = (best_scores[-1] - best_scores[0]) / best_scores[0] if best_scores[0] > 0 else 0
            if improvement < 0.05:
                self.log_message("Convergence detected: scores plateaued")
                return True
        
        # Check if we have a high-scoring idea
        if best_scores and best_scores[-1] > 0.85:
            self.log_message("Convergence detected: excellent idea found")
            return True
        
        return False
    
    def get_final_report(self) -> Dict[str, Any]:
        """Generate a final report of the ideation process"""
        if not self.iteration_history:
            return {"error": "No iterations completed"}
        
        total_ideas = sum(len(ir.generated_ideas) for ir in self.iteration_history)
        all_evaluations = [e for ir in self.iteration_history for e in ir.evaluations]
        
        best_evaluation = max(all_evaluations, key=lambda e: e.composite_score) if all_evaluations else None
        
        report = {
            "total_iterations": len(self.iteration_history),
            "total_ideas_generated": total_ideas,
            "best_score": best_evaluation.composite_score if best_evaluation else 0.0,
            "best_idea_id": best_evaluation.idea_id if best_evaluation else None,
            "average_score": sum(e.composite_score for e in all_evaluations) / len(all_evaluations) if all_evaluations else 0.0,
            "score_progression": [
                max(ir.evaluations, key=lambda e: e.composite_score).composite_score if ir.evaluations else 0.0
                for ir in self.iteration_history
            ]
        }
        
        return report

