"""
Synthesizer Agent - Merges and combines complementary ideas
"""
import json
from typing import List, Tuple
import numpy as np
from agents.base_agent import BaseAgent
from core.models import SaaSIdea
from config import config


class SynthesizerAgent(BaseAgent):
    """Agent responsible for merging complementary ideas"""
    
    def __init__(self):
        super().__init__(
            name="Synthesizer",
            model=config.SYNTHESIZER_MODEL,
            role_description="You are a product synthesis expert. Your role is to identify synergies between ideas and merge them into superior hybrid products."
        )
        self.embeddings_model = None
    
    def execute(self, ideas: List[SaaSIdea], embeddings: List[np.ndarray] = None) -> List[SaaSIdea]:
        """
        Synthesize new ideas by merging complementary ones
        
        Args:
            ideas: List of ideas to potentially merge
            embeddings: Optional pre-computed embeddings for similarity analysis
            
        Returns:
            List of synthesized SaaSIdea objects
        """
        if len(ideas) < 2:
            self.log_message("Not enough ideas to synthesize")
            return []
        
        # Find complementary pairs or clusters
        if embeddings is not None and len(embeddings) == len(ideas):
            pairs = self._find_complementary_pairs_by_embedding(ideas, embeddings)
        else:
            pairs = self._find_complementary_pairs_by_llm(ideas)
        
        # Merge each pair
        synthesized = []
        for idea1, idea2 in pairs:
            self.log_message(f"Synthesizing: {idea1.idea_name} + {idea2.idea_name}")
            merged = self._merge_ideas(idea1, idea2)
            if merged:
                synthesized.append(merged)
        
        self.log_message(f"Created {len(synthesized)} synthesized ideas")
        return synthesized
    
    def _find_complementary_pairs_by_llm(self, ideas: List[SaaSIdea]) -> List[Tuple[SaaSIdea, SaaSIdea]]:
        """Use LLM to identify complementary idea pairs"""
        prompt = self._build_pairing_prompt(ideas)
        
        response = self._call_llm(
            prompt=prompt,
            system_message="You are an expert at identifying synergies between product ideas.",
            temperature=0.4,
            max_tokens=2000
        )
        
        # Parse pairs from response
        pairs = self._parse_pairs(response, ideas)
        return pairs[:min(3, len(ideas) // 2)]  # Limit to top 3 pairs
    
    def _find_complementary_pairs_by_embedding(self, ideas: List[SaaSIdea], 
                                               embeddings: List[np.ndarray]) -> List[Tuple[SaaSIdea, SaaSIdea]]:
        """Find complementary pairs using semantic similarity"""
        pairs = []
        used_indices = set()
        
        # Calculate cosine similarities
        embeddings_array = np.array(embeddings)
        
        for i in range(len(ideas)):
            if i in used_indices:
                continue
            
            # Find most similar idea that hasn't been used
            similarities = []
            for j in range(len(ideas)):
                if i != j and j not in used_indices:
                    sim = np.dot(embeddings_array[i], embeddings_array[j]) / (
                        np.linalg.norm(embeddings_array[i]) * np.linalg.norm(embeddings_array[j])
                    )
                    similarities.append((j, sim))
            
            if similarities:
                # Get most similar (but not too similar - we want complementary, not identical)
                similarities.sort(key=lambda x: x[1], reverse=True)
                for idx, sim in similarities:
                    if 0.4 < sim < 0.8:  # Sweet spot for complementary ideas
                        pairs.append((ideas[i], ideas[idx]))
                        used_indices.add(i)
                        used_indices.add(idx)
                        break
        
        return pairs[:3]  # Top 3 pairs
    
    def _build_pairing_prompt(self, ideas: List[SaaSIdea]) -> str:
        """Build prompt for finding complementary pairs"""
        ideas_text = ""
        for idx, idea in enumerate(ideas):
            ideas_text += f"\n{idx + 1}. {idea.idea_name}\n"
            ideas_text += f"   Problem: {idea.problem_statement}\n"
            ideas_text += f"   Features: {', '.join(idea.core_features[:3])}\n"
        
        prompt = f"""Analyze these SaaS product ideas and identify pairs that would work well together if merged:

{ideas_text}

Identify 2-3 pairs of ideas that:
- Address related or complementary problems
- Could share features or infrastructure
- Would create more value combined than separate
- Target similar or adjacent user segments

Output as JSON array:
[
  {{"idea1_index": 1, "idea2_index": 3, "synergy": "Why these work together"}},
  ...
]

Your analysis:"""
        
        return prompt
    
    def _parse_pairs(self, response: str, ideas: List[SaaSIdea]) -> List[Tuple[SaaSIdea, SaaSIdea]]:
        """Parse LLM response into idea pairs"""
        pairs = []
        
        try:
            response = response.strip()
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
            
            pairs_data = json.loads(response)
            
            for pair_data in pairs_data:
                idx1 = pair_data["idea1_index"] - 1  # Convert to 0-based
                idx2 = pair_data["idea2_index"] - 1
                
                if 0 <= idx1 < len(ideas) and 0 <= idx2 < len(ideas):
                    pairs.append((ideas[idx1], ideas[idx2]))
        
        except Exception as e:
            self.log_message(f"Error parsing pairs: {e}")
        
        return pairs
    
    def _merge_ideas(self, idea1: SaaSIdea, idea2: SaaSIdea) -> SaaSIdea:
        """Merge two ideas into a synthesized hybrid with synthesis framework"""
        prompt = f"""Merge these two SaaS product ideas into a single, superior hybrid product using synthesis principles.

**Idea 1: {idea1.idea_name}**
- Problem: {idea1.problem_statement}
- Target User: {idea1.target_user}
- Core Features: {', '.join(idea1.core_features)}
- Differentiator: {idea1.differentiator}
- Tech Stack: {', '.join(idea1.tech_stack)}

**Idea 2: {idea2.idea_name}**
- Problem: {idea2.problem_statement}
- Target User: {idea2.target_user}
- Core Features: {', '.join(idea2.core_features)}
- Differentiator: {idea2.differentiator}
- Tech Stack: {', '.join(idea2.tech_stack)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**SYNTHESIS PRINCIPLES (Critical - Follow These):**

**1. COMPLEMENTARY, NOT ADDITIVE:**
❌ BAD: "Does everything Idea 1 does + everything Idea 2 does" 
   → This creates feature bloat and confused value proposition

✅ GOOD: "Solves Idea 1's core problem using Idea 2's unique approach"
   → This creates focused value through synergy

**Example:**
- Idea 1: Contract management with alerts
- Idea 2: Spend analytics with cost optimization
- ❌ Bad Merge: "Contract management + spend analytics" (two separate tools)
- ✅ Good Merge: "Contract intelligence that automatically identifies savings opportunities by analyzing renewal patterns and market benchmarks"

**2. 1 + 1 = 3 (SYNERGY TEST):**
The merged product should create NEW value not available in either original idea.

Ask yourself: "What becomes possible when these capabilities are combined?"

**Example:**
- Idea 1: Email sentiment analysis
- Idea 2: Contract dispute prediction
- Synergy: Predict disputes 90 days early by analyzing email sentiment + contract terms
- New Value: Early warning system (neither idea had this alone)

**3. UNIFIED USER JOURNEY:**
Don't create two separate workflows side-by-side. Create ONE cohesive experience.

❌ BAD: "Users can do Task A (from Idea 1) OR Task B (from Idea 2)"
✅ GOOD: "Users complete Task A which automatically triggers Task B as part of the same workflow"

**4. TARGET USER CONVERGENCE:**
If target users differ, find the overlap or pick the more valuable segment. Don't try to serve two masters.

❌ BAD: "For legal teams AND finance teams"
✅ GOOD: "For legal operations teams with procurement responsibilities"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**YOUR SYNTHESIS PROCESS:**

**Step 1: Identify the Synergy**
- What unique capability does Idea 1 have? → [Answer]
- What unique capability does Idea 2 have? → [Answer]
- How do they amplify each other? → [Answer]
- What NEW capability emerges from combination? → [Answer]

**Step 2: Define Unified Value Proposition**
- What problem does the MERGED idea solve? (Not "Problem 1 + Problem 2")
- Why is it better than using both separately?
- Can you explain it in ONE sentence?

**Step 3: Eliminate Redundancies**
- What features from each idea can be CUT without losing value?
- Which features from both ideas do the same thing?
- Keep only features that contribute to the synergy

**Step 4: Create Emergent Features**
- What becomes possible when you combine these capabilities?
- What features should exist ONLY in the merged product?

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**ANTI-PATTERNS TO AVOID:**

❌ "This product combines X and Y" (vague, no synergy)
❌ "For user group A AND user group B" (no focus)
❌ Features: [all 10 features from both ideas] (feature bloat)
❌ Differentiator just lists both differentiators (no new unique value)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**OUTPUT FORMAT:**

{{
  "idea_name": "New hybrid name that reflects the synergy, not just 'X + Y'",
  "problem_statement": "UNIFIED problem (not Problem 1 + Problem 2). Describe the combined pain point.",
  "target_user": "SPECIFIC converged user persona (pick primary segment, not 'A and B')",
  "core_features": [
    "Emergent Feature 1 (exists ONLY in merged product due to synergy)",
    "Best of Idea 1 Feature (enhanced by Idea 2's capability)",
    "Best of Idea 2 Feature (enhanced by Idea 1's capability)",
    "Feature 4 (no redundant features - each must add unique value)"
  ],
  "differentiator": "Explain the SYNERGY: 'By combining [capability 1] with [capability 2], we achieve [new outcome] that neither could do alone'",
  "tech_stack": ["Combined tech stack - remove duplicates"],
  "revenue_model": "Subscription",
  "synergy_explanation": "Explicitly state what NEW value emerges from combining these ideas",
  "merged_workflow": "Describe the UNIFIED user workflow in 2-3 sentences"
}}

**QUALITY CHECKS (before finalizing):**
□ Does the merged idea have a SINGLE, clear value proposition? (Not "does X and Y")
□ Is the target user MORE specific than either original? (Not "both personas")
□ Do features work together in one workflow? (Not separate feature lists)
□ Can you explain in ONE sentence why this is better than using both separately?
□ Does the differentiator explain SYNERGY, not just list both differentiators?

If any check fails, revise your synthesis.

**Now provide your synthesized idea:**"""
        
        try:
            response = self._call_llm(
                prompt=prompt,
                system_message=self.role_description,
                temperature=0.7,
                max_tokens=2000
            )
            
            # Parse response
            response = response.strip()
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
            
            merged_data = json.loads(response)
            
            # Create new SaaSIdea
            from core.models import RevenueModel
            
            merged_idea = SaaSIdea(
                idea_name=merged_data["idea_name"],
                problem_statement=merged_data["problem_statement"],
                target_user=merged_data["target_user"],
                core_features=merged_data["core_features"],
                differentiator=merged_data["differentiator"],
                tech_stack=merged_data["tech_stack"],
                revenue_model=RevenueModel(merged_data.get("revenue_model", "Subscription")),
                domain=idea1.domain,  # Use domain from first idea
                parent_ideas=[idea1.idea_id, idea2.idea_id]
            )
            
            return merged_idea
            
        except Exception as e:
            self.log_message(f"Error merging ideas: {e}")
            return None

