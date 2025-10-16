"""
PRD Generator Agent - Expands ideas into detailed Product Requirements Documents
"""
import json
from typing import Dict, Any
from agents.base_agent import BaseAgent
from core.models import SaaSIdea
from config import config


class PRDGeneratorAgent(BaseAgent):
    """Agent responsible for generating detailed Product Requirements Documents"""
    
    def __init__(self):
        super().__init__(
            name="PRD Generator",
            model=config.GENERATOR_MODEL,  # Use same model as generator
            role_description="You are a senior product manager expert at creating comprehensive Product Requirements Documents (PRDs). You transform high-level product ideas into detailed, actionable specifications."
        )
    
    def execute(self, idea: SaaSIdea) -> Dict[str, Any]:
        """
        Generate a comprehensive PRD for a SaaS idea using chunking strategy
        
        Args:
            idea: The SaaS idea to expand into a PRD
            
        Returns:
            Dictionary containing the complete PRD
        """
        self.log_message(f"Generating PRD for: {idea.idea_name} (using chunking strategy)")
        
        # Generate PRD in sections to avoid token limits
        prd = {
            "product_name": idea.idea_name,
            "metadata": {
                "idea_id": idea.idea_id,
                "generated_by": self.name,
                "version": "1.0",
                "generation_method": "chunked"
            }
        }
        
        # Section 1: Executive Summary & Problem
        print("   📝 Generating: Executive Summary & Problem Statement...")
        prd.update(self._generate_executive_and_problem(idea))
        
        # Section 2: Features & UX
        print("   📝 Generating: Features & User Experience...")
        prd.update(self._generate_features(idea))
        
        # Section 3: Technical Architecture
        print("   📝 Generating: Technical Architecture...")
        prd.update(self._generate_technical(idea))
        
        # Section 4: Business Model & GTM
        print("   📝 Generating: Business Model & Go-to-Market...")
        prd.update(self._generate_business(idea))
        
        # Section 5: Roadmap & Risks
        print("   📝 Generating: Roadmap & Risk Analysis...")
        prd.update(self._generate_roadmap_and_risks(idea))
        
        self.log_message(f"PRD generated successfully for {idea.idea_name}")
        return prd
    
    def _generate_executive_and_problem(self, idea: SaaSIdea) -> Dict[str, Any]:
        """Generate executive summary and problem statement section"""
        prompt = f"""For the SaaS product "{idea.idea_name}", create the Executive Summary and Problem Statement.

**Context:**
- Problem: {idea.problem_statement}
- Target User: {idea.target_user}
- Domain: {idea.domain}
- Differentiator: {idea.differentiator}

Generate a JSON object with:
{{
  "tagline": "One compelling sentence value proposition",
  "executive_summary": {{
    "overview": "2-3 sentences describing the product, the problem it solves, and its unique value",
    "objectives": ["3-5 specific, measurable business objectives"],
    "success_metrics": ["3-5 concrete KPIs with targets and timeframes"]
  }},
  "problem_and_solution": {{
    "pain_points": ["4-6 specific pain points experienced by target users"],
    "current_alternatives": ["2-3 existing solutions and their key limitations"],
    "our_solution": "How we uniquely solve these problems (2-3 sentences)",
    "market_opportunity": "Market size and growth opportunity"
  }},
  "target_users": {{
    "primary_persona": "Detailed persona: Name, role, company size, key characteristics",
    "use_cases": ["5-7 primary use cases for the product"]
  }}
}}"""
        
        response = self._call_llm(prompt, self._build_system_message(), temperature=0.7, max_tokens=2000)
        return self._parse_json_response(response)
    
    def _generate_features(self, idea: SaaSIdea) -> Dict[str, Any]:
        """Generate features and UX section"""
        features_str = ', '.join(idea.core_features)
        prompt = f"""For the SaaS product "{idea.idea_name}", create detailed feature specifications.

**Context:**
- Core Features: {features_str}
- Target User: {idea.target_user}
- Differentiator: {idea.differentiator}

Generate a JSON object with:
{{
  "mvp_features": [
    {{
      "name": "Feature name",
      "description": "Detailed description (3-4 sentences) of what it does and why it matters",
      "user_story": "As a [specific user], I want to [specific action] so that [specific benefit]",
      "acceptance_criteria": ["Given [context], when [action], then [result]" - 2-3 criteria],
      "priority": "P0 (Must have for MVP)",
      "effort": "S/M/L with justification"
    }}
  ],
  "future_features": [
    {{
      "name": "Feature name",
      "description": "Brief description",
      "priority": "P1/P2",
      "rationale": "Why this matters post-MVP"
    }}
  ],
  "user_experience": {{
    "key_workflows": ["3-5 critical user workflows with brief steps"],
    "design_principles": ["4-6 core UX principles guiding the design"],
    "accessibility": ["3-4 key accessibility requirements"]
  }}
}}

Include 5-6 detailed MVP features and 3-4 future features."""
        
        response = self._call_llm(prompt, self._build_system_message(), temperature=0.7, max_tokens=5000)
        return self._parse_json_response(response)
    
    def _generate_technical(self, idea: SaaSIdea) -> Dict[str, Any]:
        """Generate technical architecture section"""
        tech_stack_str = ', '.join(idea.tech_stack)
        prompt = f"""For the SaaS product "{idea.idea_name}", create the technical architecture specification.

**Context:**
- Suggested Tech Stack: {tech_stack_str}
- Core Features: {', '.join(idea.core_features)}
- Domain: {idea.domain}

Generate a JSON object with:
{{
  "technical_architecture": {{
    "stack": {{
      "frontend": "Technology choices with 1-sentence rationale",
      "backend": "Technology choices with 1-sentence rationale",
      "database": "Database choice with 1-sentence rationale",
      "ai_ml": "AI/ML models and services to be used",
      "infrastructure": "Cloud platform and deployment approach"
    }},
    "key_integrations": [
      {{
        "system": "System name (e.g., Slack, Salesforce)",
        "purpose": "Why we integrate",
        "priority": "P0/P1/P2"
      }}
    ],
    "security_requirements": ["5-7 specific security requirements"],
    "performance_targets": [
      "Page load: < X ms",
      "API response: < X ms",
      "Uptime: X%",
      "Concurrent users: X"
    ],
    "scalability_plan": ["3-4 key scalability considerations"]
  }},
  "data_model": {{
    "key_entities": [
      {{
        "entity": "Entity name",
        "attributes": ["Key attributes"],
        "relationships": ["Relationships to other entities"]
      }}
    ],
    "data_retention": "Policy description",
    "compliance": ["Compliance requirements: GDPR, SOC 2, etc."]
  }}
}}"""
        
        response = self._call_llm(prompt, self._build_system_message(), temperature=0.6, max_tokens=4500)
        return self._parse_json_response(response)
    
    def _generate_business(self, idea: SaaSIdea) -> Dict[str, Any]:
        """Generate business model and GTM section"""
        prompt = f"""For the SaaS product "{idea.idea_name}", create the business model and go-to-market strategy.

**Context:**
- Revenue Model: {idea.revenue_model}
- Target User: {idea.target_user}
- Domain: {idea.domain}

Generate a JSON object with:
{{
  "business_model": {{
    "revenue_model": "Specific model: subscription/usage-based/hybrid",
    "pricing_tiers": [
      {{
        "name": "Tier name (e.g., Starter, Professional, Enterprise)",
        "price": "$X/month or seat",
        "target": "Specific target segment",
        "key_features": ["3-5 included features"],
        "limits": "Usage limits or seat count"
      }}
    ],
    "unit_economics": {{
      "cac_estimate": "$X - estimated customer acquisition cost",
      "ltv_estimate": "$Y - estimated lifetime value",
      "payback_period": "Z months - time to recover CAC",
      "gross_margin": "XX% - estimated gross margin"
    }},
    "cost_structure": {{
      "fixed_costs": ["Key fixed cost items"],
      "variable_costs": ["Cost per user/transaction"]
    }}
  }},
  "go_to_market": {{
    "launch_strategy": "Detailed 2-3 sentence launch approach",
    "primary_channels": [
      {{
        "channel": "Channel name",
        "strategy": "How we'll use it",
        "priority": "P0/P1"
      }}
    ],
    "key_messaging": ["3-4 core marketing messages"],
    "early_adopter_strategy": "How we'll get first 100 customers",
    "sales_motion": "Product-led growth / Sales-led / Hybrid - with details"
  }}
}}

Include 3-4 pricing tiers with realistic prices."""
        
        response = self._call_llm(prompt, self._build_system_message(), temperature=0.7, max_tokens=3000)
        return self._parse_json_response(response)
    
    def _generate_roadmap_and_risks(self, idea: SaaSIdea) -> Dict[str, Any]:
        """Generate roadmap and risk analysis section"""
        prompt = f"""For the SaaS product "{idea.idea_name}", create the roadmap and risk analysis.

**Context:**
- Product: {idea.idea_name}
- Domain: {idea.domain}
- Core Features: {', '.join(idea.core_features)}

Generate a JSON object with:
{{
  "roadmap": {{
    "mvp_phase": {{
      "timeline": "X weeks/months with target date",
      "milestones": ["4-5 specific milestones with deliverables"],
      "success_criteria": "What defines MVP success"
    }},
    "growth_phase": {{
      "timeline": "X months (after MVP)",
      "milestones": ["4-5 key growth milestones"],
      "focus": "Primary focus areas"
    }},
    "scale_phase": {{
      "timeline": "X months (after growth)",
      "milestones": ["3-4 scaling milestones"],
      "focus": "Key scaling initiatives"
    }}
  }},
  "risks_and_mitigations": [
    {{
      "risk": "Specific risk description",
      "category": "Technical/Market/Business/Regulatory",
      "impact": "High/Medium/Low with explanation",
      "probability": "High/Medium/Low",
      "mitigation": "Detailed mitigation strategy"
    }}
  ],
  "dependencies": [
    {{
      "dependency": "What we depend on",
      "type": "Technical/Business/Legal/Partnership",
      "criticality": "High/Medium/Low",
      "mitigation": "How we address if unavailable"
    }}
  ],
  "competitive_advantage": {{
    "main_competitors": ["2-3 primary competitors"],
    "their_strengths": ["What they do well"],
    "their_weaknesses": ["Their key limitations"],
    "our_differentiators": ["4-5 specific advantages we have"],
    "defensibility": "How we maintain our advantage"
  }}
}}

Include 5-6 risks and 3-4 dependencies."""
        
        response = self._call_llm(prompt, self._build_system_message(), temperature=0.7, max_tokens=4500)
        return self._parse_json_response(response)
    
    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON response from LLM"""
        try:
            response = response.strip()
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
            
            return json.loads(response)
        except Exception as e:
            print(f"      ⚠️  Warning: Failed to parse section: {str(e)}")
            return {"error": str(e), "raw_response": response[:200]}
    
    def _build_system_message(self) -> str:
        """Build system message for PRD generation"""
        return """You are a world-class product manager with 15+ years of experience at top tech companies (Google, Amazon, Microsoft). 

Your expertise includes:
- Writing clear, comprehensive Product Requirements Documents
- Breaking down complex products into detailed features
- Defining user stories and acceptance criteria
- Specifying technical requirements
- Creating realistic roadmaps
- Identifying risks and dependencies

You write PRDs that engineering teams love because they are:
- Specific and actionable
- Technically feasible
- User-focused
- Complete but concise
- Easy to understand"""
    
    def _build_prd_prompt(self, idea: SaaSIdea) -> str:
        """Build prompt for PRD generation"""
        prompt = f"""Create a comprehensive Product Requirements Document (PRD) for the following SaaS product idea:

**Product Idea:**
- Name: {idea.idea_name}
- Problem Statement: {idea.problem_statement}
- Target User: {idea.target_user}
- Core Features: {', '.join(idea.core_features)}
- Differentiator: {idea.differentiator}
- Tech Stack: {', '.join(idea.tech_stack)}
- Revenue Model: {idea.revenue_model}
- Domain: {idea.domain}

**Your Task:**
Generate a detailed, production-ready PRD. Be comprehensive but concise - aim for clarity over verbosity. Output as valid JSON.

{{
  "product_name": "Product name",
  "tagline": "One-line value proposition",
  
  "executive_summary": {{
    "overview": "2-3 sentences describing the product and its value",
    "objectives": ["3-5 key business objectives"],
    "success_metrics": ["3-5 measurable targets with timeframes"]
  }},
  
  "problem_and_solution": {{
    "pain_points": ["3-5 specific user pain points"],
    "current_alternatives": ["2-3 alternatives and their limitations"],
    "our_solution": "How we solve it differently"
  }},
  
  "target_users": {{
    "primary_persona": "Name (e.g., Sarah the Compliance Manager) - role, company size, key needs",
    "use_cases": ["3-5 primary use cases"]
  }},
  
  "mvp_features": [
    {{
      "name": "Feature name",
      "description": "What it does (2-3 sentences)",
      "user_story": "As a [user], I want to [action] so that [benefit]",
      "priority": "P0/P1/P2",
      "effort": "S/M/L"
    }}
  ],
  
  "technical_architecture": {{
    "stack": {{
      "frontend": "Technology and why",
      "backend": "Technology and why",
      "database": "Technology and why",
      "ai_ml": "Models and services used"
    }},
    "key_integrations": ["3-5 critical integrations"],
    "security": ["3-5 key security requirements"],
    "performance_targets": ["Response time, uptime, scale targets"]
  }},
  
  "business_model": {{
    "pricing_tiers": [
      {{
        "name": "Tier name",
        "price": "$X/month",
        "target": "Who it's for",
        "key_features": ["3-5 included features"]
      }}
    ],
    "unit_economics": "CAC: $X, LTV: $Y, Payback: Z months"
  }},
  
  "go_to_market": {{
    "launch_strategy": "2-3 sentences on launch approach",
    "primary_channels": ["3-4 acquisition channels"],
    "key_messaging": ["2-3 core messages"]
  }},
  
  "roadmap": {{
    "mvp_phase": {{
      "timeline": "X months",
      "milestones": ["3-4 key milestones"]
    }},
    "growth_phase": {{
      "timeline": "X months after MVP",
      "milestones": ["3-4 key milestones"]
    }}
  }},
  
  "risks": [
    {{
      "risk": "Risk description",
      "impact": "H/M/L",
      "mitigation": "How we address it"
    }}
  ],
  
  "competitive_advantage": {{
    "competitors": ["2-3 main competitors"],
    "our_differentiators": ["3-4 key advantages"]
  }}
}}

**Requirements:**
- Be SPECIFIC with numbers, tech choices, and timelines
- Include 5-7 detailed MVP features
- Make it actionable - engineering can start immediately
- Focus on the most critical information

Generate the complete PRD now:"""
        
        return prompt
    
    def _parse_prd(self, response: str, idea: SaaSIdea) -> Dict[str, Any]:
        """Parse PRD response"""
        try:
            # Extract JSON from response
            response = response.strip()
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
            
            prd = json.loads(response)
            
            # Add metadata
            prd["metadata"] = {
                "idea_id": idea.idea_id,
                "idea_name": idea.idea_name,
                "generated_by": self.name,
                "version": "1.0"
            }
            
            return prd
            
        except Exception as e:
            self.log_message(f"Error parsing PRD: {e}")
            # Return a basic structure if parsing fails
            return {
                "product_name": idea.idea_name,
                "error": f"Failed to parse complete PRD: {str(e)}",
                "raw_response": response[:500]
            }
    
    def generate_feature_deep_dive(self, idea: SaaSIdea, feature_name: str) -> Dict[str, Any]:
        """
        Generate a deep dive on a specific feature
        
        Args:
            idea: The SaaS idea
            feature_name: Name of the feature to expand
            
        Returns:
            Detailed feature specification
        """
        prompt = f"""Create a detailed specification for this feature:

**Product:** {idea.idea_name}
**Feature:** {feature_name}

Provide a comprehensive feature specification including:

{{
  "feature_name": "{feature_name}",
  "overview": "What this feature does and why it matters",
  
  "user_stories": [
    "As a [user], I want to [action] so that [benefit]"
  ],
  
  "functional_requirements": [
    "The system shall..."
  ],
  
  "user_interface": {{
    "screens": [
      {{
        "screen_name": "Screen name",
        "components": ["Component 1", "Component 2"],
        "interactions": ["User can...", "System will..."]
      }}
    ],
    "wireframe_description": "Detailed description of layout"
  }},
  
  "technical_implementation": {{
    "frontend": ["Implementation details"],
    "backend": ["API endpoints", "Logic"],
    "database": ["Tables", "Fields"],
    "apis": ["External APIs needed"]
  }},
  
  "acceptance_criteria": [
    "Given [context], when [action], then [expected result]"
  ],
  
  "edge_cases": [
    "What happens if..."
  ],
  
  "testing_strategy": {{
    "unit_tests": ["Test 1", "..."],
    "integration_tests": ["Test 1", "..."],
    "user_acceptance_tests": ["Scenario 1", "..."]
  }},
  
  "implementation_steps": [
    {{
      "step": 1,
      "task": "Task description",
      "estimated_hours": X
    }}
  ],
  
  "dependencies": ["Dependency 1", "..."],
  
  "risks": ["Risk 1", "..."]
}}

Output as valid JSON:"""
        
        response = self._call_llm(
            prompt=prompt,
            system_message=self.role_description,
            temperature=0.6,
            max_tokens=4000
        )
        
        try:
            response = response.strip()
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
            
            return json.loads(response)
        except:
            return {"feature_name": feature_name, "error": "Failed to parse", "raw": response[:500]}

