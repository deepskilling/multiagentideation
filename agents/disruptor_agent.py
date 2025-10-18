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
        """Disrupt by removing traditional constraints with Christensen's disruption theory"""
        prompt = f"""Take this SaaS idea and reimagine it by removing a major constraint using disruption theory.

**Original Idea: {idea.idea_name}**
- Problem: {idea.problem_statement}
- Features: {', '.join(idea.core_features)}
- Target: {idea.target_user}
- Domain: {idea.domain}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**DISRUPTION THEORY (Clayton Christensen Framework):**

Disruptive innovations typically:

1. **Target Overserved Customers**
   - Who doesn't need ALL the features incumbents offer?
   - Who values simplicity/affordability over sophistication?
   
2. **Offer "Good Enough" Solutions**
   - Meet core needs at 10x lower cost/complexity
   - Trade some performance for accessibility
   
3. **Start in Neglected Segments**
   - Non-consumers (people who can't use existing solutions)
   - Overshot customers (those who pay for features they don't use)
   - New market footholds (emerging segments)
   
4. **Compete on Different Dimensions**
   - Incumbents compete on: Performance, features, enterprise capabilities
   - Disruptors compete on: Simplicity, speed, affordability, accessibility

**Classic Disruption Pattern:**
- Incumbents move upmarket (more features, higher prices)
- Disruptors enter low-end (simpler, cheaper)
- Disruptors improve and move upmarket over time
- Incumbents can't respond (profit margins too low)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**CONSTRAINT REMOVAL ANALYSIS:**

**Step 1: Identify constraints in current solutions (including this idea)**
Ask:
- What makes existing tools expensive? 
  → Enterprise sales, complex setup, training, integrations
  
- What makes them slow? 
  → Manual processes, approval workflows, custom implementations
  
- What makes them limited? 
  → Data silos, platform lock-in, access restrictions, technical requirements

**Step 2: Choose ONE critical constraint to remove**

Examples of Disruptive Constraint Removals:

✅ **Remove Integration Complexity:**
- Traditional: Requires IT team to configure APIs and data mappings
- Disruptive: Automatically reads existing data stores (no integration needed)
- Impact: Deployment from 6 months → 30 minutes

✅ **Remove Technical Requirements:**
- Traditional: Requires dedicated infrastructure, security setup, admin training
- Disruptive: Runs as browser extension, no infrastructure, zero setup
- Impact: Open to 10x more users (no IT approval needed)

✅ **Remove Cost Barrier:**
- Traditional: $50K/year enterprise license
- Disruptive: Open-source core + $99/month for hosting
- Impact: Accessible to SMBs (95% of market can't afford traditional)

✅ **Remove Expertise Requirement:**
- Traditional: Requires data scientists to configure ML models
- Disruptive: AI auto-configures based on your data
- Impact: Non-technical users can use advanced features

❌ **Don't Just Remove Randomly:**
- Bad: "What if it was free?" (need revenue model)
- Bad: "What if it needed no data?" (need data to provide value)
- Good: "What if it needed no DATA INTEGRATION?" (data can live where it is)

**Step 3: Redesign around that constraint removal**
- What features become POSSIBLE?
- What features become UNNECESSARY?
- What new market opens up?

**Step 4: Validate disruption feasibility**
- Is the constraint removal technically possible TODAY?
- Does it create real NEW value (not just reduce friction)?
- Can you build a business around this (or is it just a feature)?
- Is there a 10x improvement on some dimension?

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**YOUR TASK:**

Using the original idea as inspiration, create a disruptive variation by removing a constraint.

Think through:
1. What's the biggest barrier preventing 10x more people from using this type of product?
2. Which constraint removal would create 10x improvement on SOME dimension (cost, speed, ease)?
3. What becomes possible that wasn't before?

Output as JSON:
{{
  "idea_name": "Disrupted product name",
  "problem_statement": "Refined problem that's accessible to more users",
  "target_user": "Expanded target (who couldn't use the original?)",
  "core_features": [
    "Feature enabled by constraint removal",
    "Simplified version of original feature",
    "Feature 3"
  ],
  "differentiator": "Unlike [incumbents], we remove [constraint] by [approach], enabling [new capability]",
  "tech_stack": ["Technology 1", "Technology 2"],
  "revenue_model": "Freemium|Usage-Based (likely different from original)",
  "disruption_analysis": {{
    "constraint_removed": "Specific constraint eliminated",
    "how_removed": "Technical approach to removing it",
    "new_market_opened": "Who can now use this who couldn't before?",
    "10x_dimension": "What is 10x better? (cost, speed, ease, access)",
    "incumbent_weakness": "Why can't incumbents easily respond?"
  }}
}}

**QUALITY CHECKS:**
□ Is there a SPECIFIC constraint removed (not vague "more accessible")?
□ Does removal enable 10x improvement on SOME dimension?
□ Can you identify WHO specifically can now use this who couldn't before?
□ Is the disruption technically feasible in 2025?
□ Would incumbents struggle to copy this? (profit margins, architecture, business model)

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

