"""
Disruptor Agent - Challenges assumptions and creates bold variations
"""
import json
from typing import List
from agents.base_agent import BaseAgent
from core.models import SaaSIdea, RevenueModel
from config import config


class DisruptorAgent(BaseAgent):
    """Agent responsible for disrupting conventional thinking and creating bold variations"""
    
    def __init__(self):
        super().__init__(
            name="Disruptor",
            model=config.DISRUPTOR_MODEL,
            role_description="You are a disruptive innovation expert. Your role is to challenge conventional assumptions and create bold, unconventional variations of product ideas."
        )
    
    def execute(self, ideas: List[SaaSIdea]) -> List[SaaSIdea]:
        """
        Create disruptive variations of existing ideas
        
        Args:
            ideas: List of ideas to disrupt
            
        Returns:
            List of disrupted SaaSIdea objects
        """
        disrupted_ideas = []
        
        for idea in ideas:
            self.log_message(f"Disrupting idea: {idea.idea_name}")
            disrupted = self._disrupt_idea(idea)
            if disrupted:
                disrupted_ideas.append(disrupted)
        
        self.log_message(f"Created {len(disrupted_ideas)} disrupted variations")
        return disrupted_ideas
    
    def _disrupt_idea(self, idea: SaaSIdea) -> SaaSIdea:
        """Create a disruptive variation of an idea"""
        
        # Randomly choose a disruption strategy
        import random
        strategies = [
            self._disrupt_by_removing_constraints,
            self._disrupt_by_extreme_simplification,
            self._disrupt_by_democratization,
            self._disrupt_by_ai_augmentation,
            self._disrupt_by_business_model
        ]
        
        strategy = random.choice(strategies)
        return strategy(idea)
    
    def _disrupt_by_removing_constraints(self, idea: SaaSIdea) -> SaaSIdea:
        """Disrupt by removing traditional constraints"""
        prompt = f"""Take this SaaS idea and reimagine it by removing a major constraint:

**Original Idea: {idea.idea_name}**
- Problem: {idea.problem_statement}
- Features: {', '.join(idea.core_features)}
- Target: {idea.target_user}

**Disruption Strategy**: Remove major constraints
Ask "What if..." and challenge assumptions:
- What if it was completely free?
- What if it required no setup or configuration?
- What if it worked offline?
- What if it needed no user data?
- What if deployment took 30 seconds?

Create a bold variation that removes a significant constraint and reimagines the product.

Output as JSON:
{{
  "idea_name": "Disrupted product name",
  "problem_statement": "Refined problem statement",
  "target_user": "Target user",
  "core_features": ["Feature 1", "Feature 2", "Feature 3"],
  "differentiator": "What makes this disruptive variation unique",
  "tech_stack": ["Tech 1", "Tech 2"],
  "revenue_model": "Subscription"
}}

Your disruptive variation:"""
        
        return self._execute_disruption(prompt, idea)
    
    def _disrupt_by_extreme_simplification(self, idea: SaaSIdea) -> SaaSIdea:
        """Disrupt by extreme simplification"""
        prompt = f"""Take this SaaS idea and create a radically simplified version:

**Original Idea: {idea.idea_name}**
- Problem: {idea.problem_statement}
- Features: {', '.join(idea.core_features)}
- Target: {idea.target_user}

**Disruption Strategy**: Extreme Simplification
- Remove 80% of features
- Focus on ONE core problem
- Make it 10x easier to use
- Target non-technical users if possible

Create a simplified variation that does one thing exceptionally well.

Output as JSON:
{{
  "idea_name": "Simplified product name",
  "problem_statement": "Focused problem statement",
  "target_user": "Target user",
  "core_features": ["Feature 1", "Feature 2"],
  "differentiator": "Radical simplicity",
  "tech_stack": ["Tech 1", "Tech 2"],
  "revenue_model": "Freemium"
}}

Your simplified variation:"""
        
        return self._execute_disruption(prompt, idea)
    
    def _disrupt_by_democratization(self, idea: SaaSIdea) -> SaaSIdea:
        """Disrupt by democratizing access"""
        prompt = f"""Take this SaaS idea and democratize it for a broader audience:

**Original Idea: {idea.idea_name}**
- Problem: {idea.problem_statement}
- Features: {', '.join(idea.core_features)}
- Target: {idea.target_user}

**Disruption Strategy**: Democratization
- Make it accessible to non-experts
- Remove technical barriers
- Bring enterprise features to SMBs
- Enable self-service
- Make it affordable for individuals

Create a democratized variation that opens this up to 10x more users.

Output as JSON:
{{
  "idea_name": "Democratized product name",
  "problem_statement": "Accessible problem statement",
  "target_user": "Broader target user",
  "core_features": ["Feature 1", "Feature 2", "Feature 3"],
  "differentiator": "Accessibility and democratization",
  "tech_stack": ["Tech 1", "Tech 2"],
  "revenue_model": "Freemium"
}}

Your democratized variation:"""
        
        return self._execute_disruption(prompt, idea)
    
    def _disrupt_by_ai_augmentation(self, idea: SaaSIdea) -> SaaSIdea:
        """Disrupt by adding AI capabilities"""
        prompt = f"""Take this SaaS idea and reimagine it with AI at its core:

**Original Idea: {idea.idea_name}**
- Problem: {idea.problem_statement}
- Features: {', '.join(idea.core_features)}
- Target: {idea.target_user}

**Disruption Strategy**: AI-First Reimagining
- What could AI automate completely?
- How could AI provide predictive insights?
- Can AI reduce manual work by 90%?
- Can AI personalize the experience?

Create an AI-augmented variation that leverages ML/AI to transform the product.

Output as JSON:
{{
  "idea_name": "AI-powered product name",
  "problem_statement": "AI-enhanced problem statement",
  "target_user": "Target user",
  "core_features": ["AI Feature 1", "AI Feature 2", "Feature 3"],
  "differentiator": "AI-powered automation and intelligence",
  "tech_stack": ["Python", "TensorFlow/PyTorch", "Tech 3"],
  "revenue_model": "Usage-Based"
}}

Your AI-augmented variation:"""
        
        return self._execute_disruption(prompt, idea)
    
    def _disrupt_by_business_model(self, idea: SaaSIdea) -> SaaSIdea:
        """Disrupt by changing the business model"""
        prompt = f"""Take this SaaS idea and disrupt it with a radically different business model:

**Original Idea: {idea.idea_name}**
- Problem: {idea.problem_statement}
- Features: {', '.join(idea.core_features)}
- Revenue Model: {idea.revenue_model}

**Disruption Strategy**: Business Model Innovation
- Open source with paid support?
- Marketplace/platform model?
- Pay-for-performance?
- Community-driven?
- Reverse auction?

Create a variation with an unconventional business model.

Output as JSON:
{{
  "idea_name": "Reimagined product name",
  "problem_statement": "Problem statement",
  "target_user": "Target user",
  "core_features": ["Feature 1", "Feature 2", "Feature 3"],
  "differentiator": "Innovative business model",
  "tech_stack": ["Tech 1", "Tech 2"],
  "revenue_model": "Hybrid"
}}

Your business model disruption:"""
        
        return self._execute_disruption(prompt, idea)
    
    def _execute_disruption(self, prompt: str, original_idea: SaaSIdea) -> SaaSIdea:
        """Execute a disruption strategy"""
        try:
            response = self._call_llm(
                prompt=prompt,
                system_message=self.role_description,
                temperature=0.9,  # High temperature for creative disruption
                max_tokens=2000
            )
            
            # Parse response
            response = response.strip()
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
            
            disrupted_data = json.loads(response)
            
            disrupted_idea = SaaSIdea(
                idea_name=disrupted_data["idea_name"],
                problem_statement=disrupted_data["problem_statement"],
                target_user=disrupted_data["target_user"],
                core_features=disrupted_data["core_features"],
                differentiator=disrupted_data["differentiator"],
                tech_stack=disrupted_data["tech_stack"],
                revenue_model=RevenueModel(disrupted_data.get("revenue_model", "Subscription")),
                domain=original_idea.domain,
                parent_ideas=[original_idea.idea_id]
            )
            
            return disrupted_idea
            
        except Exception as e:
            self.log_message(f"Error disrupting idea: {e}")
            return None

