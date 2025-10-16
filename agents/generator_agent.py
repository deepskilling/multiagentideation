"""
Generator Agent - Creates novel SaaS product ideas
"""
import json
from typing import List
from agents.base_agent import BaseAgent
from core.models import SaaSIdea, Domain, RevenueModel
from config import config


class GeneratorAgent(BaseAgent):
    """Agent responsible for generating innovative SaaS product ideas"""
    
    def __init__(self):
        super().__init__(
            name="Generator",
            model=config.GENERATOR_MODEL,
            role_description="You are a creative SaaS product ideation expert. Your role is to generate innovative, novel software-as-a-service product ideas that solve real enterprise pain points."
        )
    
    def execute(self, domain: str, context: str = "", num_ideas: int = 5) -> List[SaaSIdea]:
        """
        Generate SaaS product ideas for a given domain
        
        Args:
            domain: The domain/industry to focus on
            context: Additional context or constraints
            num_ideas: Number of ideas to generate
            
        Returns:
            List of SaaSIdea objects
        """
        prompt = self._build_prompt(domain, context, num_ideas)
        system_message = self._build_system_message()
        
        self.log_message(f"Generating {num_ideas} ideas for domain: {domain}")
        
        response = self._call_llm(
            prompt=prompt,
            system_message=system_message,
            temperature=0.8,  # Higher temperature for creativity
            max_tokens=4000
        )
        
        # Parse the response and create SaaSIdea objects
        ideas = self._parse_response(response, domain)
        
        self.log_message(f"Successfully generated {len(ideas)} ideas")
        return ideas
    
    def _build_system_message(self) -> str:
        """Build the system message for the LLM"""
        return """You are an expert SaaS product strategist and innovator with deep knowledge of:
- Enterprise software pain points
- Emerging technologies (AI, Cloud, Automation)
- Market trends and opportunities
- Product differentiation strategies
- Modern tech stacks and architectures

Your goal is to generate innovative, feasible, and market-ready SaaS product ideas that:
1. Solve real, validated enterprise problems
2. Have clear differentiators from existing solutions
3. Leverage modern technologies appropriately
4. Have viable business models
5. Are technically feasible

Always think creatively but practically."""
    
    def _build_prompt(self, domain: str, context: str, num_ideas: int) -> str:
        """Build the prompt for idea generation"""
        prompt = f"""Generate {num_ideas} innovative SaaS product ideas in the {domain} domain.

{f"Additional Context: {context}" if context else ""}

For each idea, provide:
1. **Idea Name**: A compelling product name
2. **Problem Statement**: What specific pain point does this solve?
3. **Target User**: Who is the primary customer? (be specific about role/persona)
4. **Core Features**: List 3-5 essential features (as a JSON array)
5. **Differentiator**: What makes this unique compared to existing solutions?
6. **Tech Stack**: Recommended technologies (as a JSON array)
7. **Revenue Model**: Choose from: Subscription, Freemium, Usage-Based, Perpetual License, or Hybrid

Output your response as a valid JSON array with this exact structure:
[
  {{
    "idea_name": "Product Name",
    "problem_statement": "Description of the problem",
    "target_user": "Specific user persona",
    "core_features": ["Feature 1", "Feature 2", "Feature 3"],
    "differentiator": "What makes this unique",
    "tech_stack": ["Technology 1", "Technology 2"],
    "revenue_model": "Subscription"
  }}
]

Focus on:
- Real enterprise pain points that cost time/money
- Solutions that leverage AI, automation, or modern cloud capabilities
- Clear value propositions
- Practical, buildable solutions

Generate {num_ideas} ideas now:"""
        
        return prompt
    
    def _parse_response(self, response: str, domain: str) -> List[SaaSIdea]:
        """Parse LLM response into SaaSIdea objects"""
        ideas = []
        
        try:
            # Extract JSON from response (handle markdown code blocks)
            response = response.strip()
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
            
            # Parse JSON
            ideas_data = json.loads(response)
            
            # Convert to SaaSIdea objects
            for idea_data in ideas_data:
                try:
                    # Map domain string to enum
                    domain_enum = self._map_domain(domain)
                    
                    # Map revenue model to enum
                    revenue_model = RevenueModel(idea_data.get("revenue_model", "Subscription"))
                    
                    idea = SaaSIdea(
                        idea_name=idea_data["idea_name"],
                        problem_statement=idea_data["problem_statement"],
                        target_user=idea_data["target_user"],
                        core_features=idea_data["core_features"],
                        differentiator=idea_data["differentiator"],
                        tech_stack=idea_data["tech_stack"],
                        revenue_model=revenue_model,
                        domain=domain_enum
                    )
                    ideas.append(idea)
                except Exception as e:
                    self.log_message(f"Error parsing individual idea: {e}")
                    continue
                    
        except json.JSONDecodeError as e:
            self.log_message(f"JSON parsing error: {e}")
            self.log_message(f"Response was: {response[:500]}")
        except Exception as e:
            self.log_message(f"Unexpected error parsing response: {e}")
        
        return ideas
    
    def _map_domain(self, domain_str: str) -> Domain:
        """Map domain string to Domain enum"""
        domain_mapping = {
            "devops": Domain.DEVOPS,
            "cloud": Domain.CLOUD,
            "grc": Domain.GRC,
            "governance": Domain.GRC,
            "risk": Domain.GRC,
            "compliance": Domain.GRC,
            "bi": Domain.BI,
            "business intelligence": Domain.BI,
            "ai": Domain.AIML,
            "ml": Domain.AIML,
            "aiml": Domain.AIML,
            "cybersecurity": Domain.CYBERSECURITY,
            "security": Domain.CYBERSECURITY,
            "data": Domain.DATA_ANALYTICS,
            "analytics": Domain.DATA_ANALYTICS,
            "collaboration": Domain.COLLABORATION
        }
        
        domain_lower = domain_str.lower()
        for key, value in domain_mapping.items():
            if key in domain_lower:
                return value
        
        # Default to CLOUD if no match
        return Domain.CLOUD
    
    def generate_with_inspiration(self, domain: str, inspiration_ideas: List[SaaSIdea], 
                                  num_ideas: int = 5) -> List[SaaSIdea]:
        """Generate ideas inspired by existing ones (for evolution/mutation)"""
        
        # Build context from inspiration ideas
        context = "Draw inspiration from these existing ideas (but create something different):\n"
        for idx, idea in enumerate(inspiration_ideas[:3], 1):
            context += f"\n{idx}. {idea.idea_name}: {idea.problem_statement}"
        
        return self.execute(domain=domain, context=context, num_ideas=num_ideas)

