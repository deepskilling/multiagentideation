"""
Scoring Engine - Calculates novelty, diversity, and composite scores
"""
import numpy as np
from typing import List, Tuple
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from core.models import SaaSIdea, Evaluation
from config import config


class ScoringEngine:
    """Engine for computing various scores and metrics"""
    
    def __init__(self):
        # Load sentence transformer for embeddings
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.previous_embeddings = []
        self.previous_ideas = []
    
    def compute_embedding(self, idea: SaaSIdea) -> np.ndarray:
        """Compute embedding vector for an idea"""
        # Combine text fields for embedding
        text = f"{idea.idea_name}. {idea.problem_statement}. {idea.differentiator}"
        embedding = self.embedding_model.encode(text, convert_to_numpy=True)
        return embedding
    
    def compute_embeddings_batch(self, ideas: List[SaaSIdea]) -> List[np.ndarray]:
        """Compute embeddings for multiple ideas"""
        texts = [
            f"{idea.idea_name}. {idea.problem_statement}. {idea.differentiator}"
            for idea in ideas
        ]
        embeddings = self.embedding_model.encode(texts, convert_to_numpy=True)
        return [embeddings[i] for i in range(len(ideas))]
    
    def compute_novelty_score(self, idea_embedding: np.ndarray) -> float:
        """
        Compute novelty score based on semantic distance from previous ideas
        
        Args:
            idea_embedding: Embedding vector of the new idea
            
        Returns:
            Novelty score between 0 and 1 (higher = more novel)
        """
        if not self.previous_embeddings:
            return 0.8  # First ideas get good novelty score
        
        # Calculate similarities to all previous ideas
        similarities = []
        for prev_embedding in self.previous_embeddings:
            sim = np.dot(idea_embedding, prev_embedding) / (
                np.linalg.norm(idea_embedding) * np.linalg.norm(prev_embedding)
            )
            similarities.append(sim)
        
        # Novelty is inverse of maximum similarity
        max_similarity = max(similarities)
        novelty = 1.0 - max_similarity
        
        # Normalize to 0-1 range (assuming similarities range from 0.3 to 1.0)
        novelty = max(0.0, min(1.0, (novelty - 0.0) / 0.7))
        
        return novelty
    
    def compute_diversity_score(self, ideas: List[SaaSIdea], 
                                embeddings: List[np.ndarray]) -> float:
        """
        Compute diversity score for a set of ideas
        
        Args:
            ideas: List of ideas
            embeddings: Corresponding embeddings
            
        Returns:
            Diversity score between 0 and 1 (higher = more diverse)
        """
        if len(ideas) < 2:
            return 1.0
        
        # Calculate pairwise similarities
        similarities = []
        for i in range(len(embeddings)):
            for j in range(i + 1, len(embeddings)):
                sim = np.dot(embeddings[i], embeddings[j]) / (
                    np.linalg.norm(embeddings[i]) * np.linalg.norm(embeddings[j])
                )
                similarities.append(sim)
        
        # Diversity is inverse of average similarity
        avg_similarity = sum(similarities) / len(similarities)
        diversity = 1.0 - avg_similarity
        
        # Normalize
        diversity = max(0.0, min(1.0, diversity / 0.7))
        
        return diversity
    
    def compute_composite_score(self, evaluation: Evaluation) -> float:
        """
        Compute weighted composite score
        
        Args:
            evaluation: Evaluation object with individual scores
            
        Returns:
            Composite score
        """
        score = (
            config.NOVELTY_WEIGHT * evaluation.novelty +
            config.FEASIBILITY_WEIGHT * evaluation.feasibility +
            config.MARKET_FIT_WEIGHT * evaluation.market_fit +
            config.VIABILITY_WEIGHT * evaluation.viability
        )
        return score
    
    def enhance_evaluation_with_novelty(self, idea: SaaSIdea, 
                                       evaluation: Evaluation,
                                       idea_embedding: np.ndarray) -> Evaluation:
        """
        Enhance an evaluation by computing semantic novelty
        
        Args:
            idea: The SaaS idea
            evaluation: Existing evaluation (from Critic)
            idea_embedding: Pre-computed embedding
            
        Returns:
            Enhanced evaluation with novelty score
        """
        # Compute semantic novelty
        novelty_score = self.compute_novelty_score(idea_embedding)
        
        # Blend with LLM's novelty assessment (70% semantic, 30% LLM)
        blended_novelty = 0.7 * novelty_score + 0.3 * evaluation.novelty
        
        # Update evaluation
        evaluation.novelty = blended_novelty
        evaluation.calculate_composite_score(
            novelty_weight=config.NOVELTY_WEIGHT,
            feasibility_weight=config.FEASIBILITY_WEIGHT,
            market_fit_weight=config.MARKET_FIT_WEIGHT,
            viability_weight=config.VIABILITY_WEIGHT
        )
        
        return evaluation
    
    def find_duplicate_ideas(self, new_ideas: List[SaaSIdea], 
                            new_embeddings: List[np.ndarray]) -> List[Tuple[int, int, float]]:
        """
        Find potential duplicate ideas based on similarity
        
        Args:
            new_ideas: List of new ideas
            new_embeddings: Corresponding embeddings
            
        Returns:
            List of tuples (idx1, idx2, similarity) for ideas exceeding threshold
        """
        duplicates = []
        threshold = config.SIMILARITY_THRESHOLD
        
        for i in range(len(new_embeddings)):
            for j in range(i + 1, len(new_embeddings)):
                sim = np.dot(new_embeddings[i], new_embeddings[j]) / (
                    np.linalg.norm(new_embeddings[i]) * np.linalg.norm(new_embeddings[j])
                )
                if sim >= threshold:
                    duplicates.append((i, j, sim))
        
        return duplicates
    
    def update_memory(self, ideas: List[SaaSIdea], embeddings: List[np.ndarray]):
        """
        Update the memory with new ideas and embeddings
        
        Args:
            ideas: New ideas to add to memory
            embeddings: Corresponding embeddings
        """
        self.previous_ideas.extend(ideas)
        self.previous_embeddings.extend(embeddings)
    
    def get_top_k_diverse_ideas(self, ideas: List[SaaSIdea], 
                               evaluations: List[Evaluation],
                               embeddings: List[np.ndarray],
                               k: int = 5) -> List[Tuple[SaaSIdea, Evaluation]]:
        """
        Select top K ideas balancing quality and diversity
        
        Args:
            ideas: List of ideas
            evaluations: Corresponding evaluations
            embeddings: Corresponding embeddings
            k: Number of ideas to select
            
        Returns:
            List of tuples (idea, evaluation) for top K ideas
        """
        if len(ideas) <= k:
            return list(zip(ideas, evaluations))
        
        # Start with the highest scored idea
        selected_indices = []
        remaining_indices = list(range(len(ideas)))
        
        # Get best idea first
        best_idx = max(remaining_indices, key=lambda i: evaluations[i].composite_score)
        selected_indices.append(best_idx)
        remaining_indices.remove(best_idx)
        
        # Iteratively select ideas that are high quality and diverse from selected
        while len(selected_indices) < k and remaining_indices:
            best_score = -1
            best_idx = None
            
            for idx in remaining_indices:
                # Quality score
                quality = evaluations[idx].composite_score
                
                # Diversity from already selected (minimum similarity)
                min_similarity = min(
                    np.dot(embeddings[idx], embeddings[sel_idx]) / (
                        np.linalg.norm(embeddings[idx]) * np.linalg.norm(embeddings[sel_idx])
                    )
                    for sel_idx in selected_indices
                )
                diversity = 1.0 - min_similarity
                
                # Combined score (70% quality, 30% diversity)
                combined = 0.7 * quality + 0.3 * diversity
                
                if combined > best_score:
                    best_score = combined
                    best_idx = idx
            
            if best_idx is not None:
                selected_indices.append(best_idx)
                remaining_indices.remove(best_idx)
        
        return [(ideas[i], evaluations[i]) for i in selected_indices]
    
    def reset_memory(self):
        """Clear the memory of previous ideas"""
        self.previous_embeddings = []
        self.previous_ideas = []

