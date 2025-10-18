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
        """Build prompt for evaluating an idea with calibration examples"""
        
        # Add search context if available
        search_section = ""
        if search_context:
            search_section = f"\n\n**Market Intelligence (from web search):**\n{search_context}\n\n**COMPETITIVE ANALYSIS REQUIRED:**\nBased on the market intelligence above:\n1. Name 2-3 direct or adjacent competitors\n2. Compare this idea's novelty to those competitors\n3. Identify specific gaps in competitors that this idea fills\n4. Adjust your novelty and viability scores based on competitive density"
        
        prompt = f"""Evaluate the following SaaS product idea on four dimensions using calibrated scoring.

**CALIBRATION EXAMPLES (for consistent scoring across all evaluations):**

**NOVELTY CALIBRATION:**
• Score 0.9 Example: "AI that predicts contract disputes 90 days in advance using NLP analysis of email sentiment and historical litigation patterns"
  → Why: Novel application of NLP to non-obvious domain with predictive capability
  
• Score 0.5 Example: "Contract management with AI-powered search and OCR extraction"
  → Why: Incremental improvement on existing solutions, AI is becoming commodity
  
• Score 0.2 Example: "Cloud-based document storage for legal contracts with folders"
  → Why: Direct copycat of Dropbox/Box with zero differentiation

**FEASIBILITY CALIBRATION:**
• Score 0.9 Example: "Dashboard aggregating data from 3 APIs (Stripe, Salesforce, HubSpot) with custom analytics"
  → Why: Well-documented APIs, proven integration patterns, 3-6 month build with 2-3 engineers
  
• Score 0.5 Example: "Real-time video collaboration platform with AR overlays for remote teams"
  → Why: Cutting-edge tech, complex infrastructure, requires specialized ML expertise, 12+ month build
  
• Score 0.2 Example: "AGI-powered autonomous business strategy consultant that replaces C-suite executives"
  → Why: Requires technology that doesn't exist yet, unclear path to implementation

**MARKET FIT CALIBRATION:**
• Score 0.9 Example: "Automated SOC 2 compliance for SaaS companies (saves $100K+ and 6 months vs manual)"
  → Why: Hair-on-fire problem, quantified savings, clear buyer (CTO/CISO), urgent need
  
• Score 0.5 Example: "Employee engagement surveys with sentiment analysis"
  → Why: Nice-to-have, not urgent, many alternatives exist, unclear ROI
  
• Score 0.2 Example: "Social network for left-handed developers to share code snippets"
  → Why: Tiny niche, unclear problem, no willingness to pay

**VIABILITY CALIBRATION:**
• Score 0.9 Example: "API monitoring for financial services (high willingness to pay, network effects, compliance moat)"
  → Why: Can charge $50K+/year, strong retention, defensible via compliance expertise
  
• Score 0.5 Example: "Project management tool for creative agencies"
  → Why: Crowded market (Asana, Monday, etc.), hard to differentiate, low switching costs
  
• Score 0.2 Example: "Free note-taking app with no monetization plan"
  → Why: No business model, commoditized product, unclear path to revenue

---

**Product Idea to Evaluate:**
- Name: {idea.idea_name}
- Problem: {idea.problem_statement}
- Target User: {idea.target_user}
- Core Features: {', '.join(idea.core_features)}
- Differentiator: {idea.differentiator}
- Tech Stack: {', '.join(idea.tech_stack)}
- Revenue Model: {idea.revenue_model}
- Domain: {idea.domain}{search_section}

---

**EVALUATION PROCESS (Think Through Each Dimension):**

**1. NOVELTY (0.0 - 1.0):**
Step 1: List 2-3 existing competitors or similar solutions
Step 2: Identify what's truly NEW (not just "AI-powered" or "cloud-based")
Step 3: Ask: "If this launched tomorrow, would competitors say 'we should have thought of that'?"
Step 4: Compare to calibration examples above
Your Score: ___

**2. FEASIBILITY (0.0 - 1.0):**
Step 1: Identify technical risks (scale, ML accuracy, complex integrations?)
Step 2: Estimate team size needed (2 people? 20 people?)
Step 3: Estimate time to MVP (3 months? 18 months?)
Step 4: Ask: "Can a skilled 3-person team build this in 6-12 months with $500K?"
Step 5: Compare to calibration examples
Your Score: ___

**3. MARKET FIT (0.0 - 1.0):**
Step 1: Quantify the problem cost (hours wasted, revenue lost, risk incurred)
Step 2: Estimate TAM (Total Addressable Market) - is it $100M+? $1B+?
Step 3: Assess buyer urgency (hair-on-fire problem or nice-to-have?)
Step 4: Ask: "Would customers pay $10K+/year for this solution?"
Step 5: Compare to calibration examples
Your Score: ___

**4. VIABILITY (0.0 - 1.0):**
Step 1: Calculate rough unit economics (CAC, LTV, gross margin)
Step 2: Assess competitive moat (network effects? data advantage? switching costs?)
Step 3: Identify GTM risks (how hard to acquire customers?)
Step 4: Ask: "Can this realistically become a $50M+ ARR business in 5 years?"
Step 5: Compare to calibration examples
Your Score: ___

---

**Output Format (JSON):**
{{
  "novelty": 0.X,
  "novelty_confidence": "high|medium|low",
  "feasibility": 0.X,
  "feasibility_confidence": "high|medium|low",
  "market_fit": 0.X,
  "market_fit_confidence": "high|medium|low",
  "viability": 0.X,
  "viability_confidence": "high|medium|low",
  "justification": "Detailed explanation covering all four dimensions with specific reasoning for each score. Reference competitors, technical challenges, market size, and business model. Cite calibration examples where applicable.",
  "key_assumptions": ["3-4 critical assumptions your scores depend on"],
  "red_flags": ["Any major concerns that could invalidate this idea"]
}}

**Confidence Levels:**
- High: Based on clear evidence, well-established patterns, or market data
- Medium: Requires assumptions but they're reasonable
- Low: High uncertainty, needs significant validation

Provide your calibrated evaluation now:"""
        
        return prompt
    
    def _parse_evaluation(self, response: str, idea: SaaSIdea) -> Evaluation:
        """Parse evaluation response into Evaluation object (with optional confidence fields)"""
        try:
            # Extract JSON from response
            response = response.strip()
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
            
            eval_data = json.loads(response)
            
            # Build justification with confidence levels and additional context
            justification = eval_data.get("justification", "")
            
            # Add confidence levels if present
            if any(k in eval_data for k in ["novelty_confidence", "feasibility_confidence", "market_fit_confidence", "viability_confidence"]):
                justification += "\n\n**Confidence Levels:**\n"
                for dim in ["novelty", "feasibility", "market_fit", "viability"]:
                    conf_key = f"{dim}_confidence"
                    if conf_key in eval_data:
                        justification += f"- {dim.replace('_', ' ').title()}: {eval_data[conf_key]}\n"
            
            # Add key assumptions if present
            if "key_assumptions" in eval_data and eval_data["key_assumptions"]:
                justification += "\n**Key Assumptions:**\n"
                for assumption in eval_data["key_assumptions"]:
                    justification += f"- {assumption}\n"
            
            # Add red flags if present
            if "red_flags" in eval_data and eval_data["red_flags"]:
                justification += "\n**Red Flags:**\n"
                for flag in eval_data["red_flags"]:
                    justification += f"- {flag}\n"
            
            evaluation = Evaluation(
                idea_id=idea.idea_id,
                novelty=float(eval_data["novelty"]),
                feasibility=float(eval_data["feasibility"]),
                market_fit=float(eval_data["market_fit"]),
                viability=float(eval_data["viability"]),
                justification=justification.strip(),
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

