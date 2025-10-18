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
        """Build the prompt for idea generation with few-shot examples"""
        prompt = f"""Generate {num_ideas} innovative SaaS product ideas in the {domain} domain.

{f"Additional Context: {context}" if context else ""}

**EXAMPLE OF A STRONG IDEA (use this as reference):**
{{
  "idea_name": "ContractIQ",
  "problem_statement": "Mid-market companies waste 40+ hours/month manually tracking contract renewals, leading to $50K+ in missed savings opportunities and compliance risks from expired vendor agreements",
  "target_user": "VP of Procurement and Legal Operations Managers at mid-market companies (500-5000 employees) managing 50-500 vendor contracts annually",
  "core_features": [
    "AI-powered contract ingestion that auto-extracts key dates, obligations, and spend data",
    "Proactive renewal alerts with cost optimization recommendations",
    "Compliance risk dashboard with auto-flagging of regulatory violations",
    "Vendor benchmarking and spend analytics"
  ],
  "differentiator": "Unlike generic CLM tools, ContractIQ is purpose-built for mid-market teams with AI that learns company-specific contract patterns and provides actionable cost-saving recommendations, not just storage",
  "tech_stack": ["Python/FastAPI", "PostgreSQL", "OpenAI GPT-4", "React", "AWS"],
  "revenue_model": "Subscription"
}}

**WHY THIS IS STRONG:**
- Problem is QUANTIFIED: $50K savings, 40+ hours wasted (specific numbers)
- Target user is HYPER-SPECIFIC: exact role, company size (500-5000), contract volume (50-500)
- Differentiator COMPARES to alternatives: "Unlike generic CLM tools..." and explains "why us"
- Features are OUTCOME-FOCUSED: what the user achieves, not just technical capabilities
- Tech stack is REALISTIC and MODERN: proven technologies that work together

---

**YOUR TASK - Generate {num_ideas} ideas following this quality standard:**

For EACH idea, follow this process:

**STEP 1 - Identify a Painful Problem:**
- What specific workflow is broken or inefficient?
- What does it cost in time/money/risk? (QUANTIFY IT)
- Why haven't existing solutions fixed this?

**STEP 2 - Define the User (Be Hyper-Specific):**
- Exact role/title (not generic "enterprise" or "developer")
- Company size and industry characteristics
- Volume/scale they operate at (e.g., "managing 50-500 contracts")
- Their decision-making authority

**STEP 3 - Design the Solution:**
- What ONE core insight makes this different?
- What specific features deliver that insight?
- Why can't competitors easily copy this?

**STEP 4 - Validate Business Viability:**
- Is the problem expensive enough that users will pay?
- Can this be built in 6-12 months?
- Is there a clear path to $10M+ ARR?

Output your response as a valid JSON array with this exact structure:
[
  {{
    "idea_name": "Product Name",
    "problem_statement": "Description with QUANTIFIED impact (time, money, risk)",
    "target_user": "SPECIFIC role at SPECIFIC company size with SPECIFIC volume/scale",
    "core_features": ["Outcome-focused feature 1", "Outcome-focused feature 2", "Feature 3"],
    "differentiator": "Unlike [competitor], we [unique approach] because [why it matters]",
    "tech_stack": ["Technology 1", "Technology 2", "Technology 3"],
    "revenue_model": "Subscription"
  }}
]

**QUALITY CHECKS (before finalizing):**
□ Does the problem statement include NUMBERS (hours, dollars, or risks)?
□ Is the target_user SPECIFIC (role + company size + volume/scale)?
□ Does the differentiator COMPARE to existing solutions (not just say "AI-powered")?
□ Are features OUTCOME-focused ("reduce X by Y%"), not technology-focused?

Generate {num_ideas} high-quality ideas now:"""
        
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

