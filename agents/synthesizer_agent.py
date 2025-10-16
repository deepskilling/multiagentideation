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
        """Merge two ideas into a synthesized hybrid"""
        prompt = f"""Merge these two SaaS product ideas into a single, superior hybrid product:

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

Create a merged product that:
1. Combines the best features from both
2. Addresses both problem spaces cohesively
3. Creates new value from the combination
4. Has a unified, compelling vision

Output as JSON:
{{
  "idea_name": "New hybrid product name",
  "problem_statement": "Unified problem statement",
  "target_user": "Target user persona",
  "core_features": ["Feature 1", "Feature 2", "Feature 3", "Feature 4"],
  "differentiator": "What makes this hybrid unique",
  "tech_stack": ["Tech 1", "Tech 2", "Tech 3"],
  "revenue_model": "Subscription"
}}

Your synthesized idea:"""
        
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

