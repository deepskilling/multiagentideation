"""
Orchestrator - Central controller for the multi-agent creativity system
"""
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path

from config import config
from core.models import SaaSIdea, Evaluation, IterationResult, Domain
from core.database import IdeaDatabase
from core.scoring import ScoringEngine
from agents import (
    GeneratorAgent,
    CriticAgent,
    SynthesizerAgent,
    DisruptorAgent,
    StrategistAgent
)


class CreativityOrchestrator:
    """Central orchestrator for the multi-agent creativity loop"""
    
    def __init__(self, db_path: Optional[Path] = None, use_web_search: bool = False):
        """Initialize the orchestrator and all agents"""
        # Initialize database
        self.db = IdeaDatabase(db_path)
        
        # Initialize scoring engine
        self.scoring_engine = ScoringEngine()
        
        # Initialize agents (with web search if enabled)
        self.use_web_search = use_web_search
        self.generator = GeneratorAgent()
        self.critic = CriticAgent(use_web_search=use_web_search)
        self.synthesizer = SynthesizerAgent()
        self.disruptor = DisruptorAgent()
        self.strategist = StrategistAgent()
        
        # State
        self.current_iteration = 0
        self.total_ideas = 0
        self.best_score = 0.0
        self.converged = False
        
        print("🚀 Multi-Agent Creativity System Initialized")
        print(f"   Generator: {self.generator.model}")
        print(f"   Critic: {self.critic.model}")
        print(f"   Synthesizer: {self.synthesizer.model}")
        print(f"   Disruptor: {self.disruptor.model}")
        print(f"   Strategist: {self.strategist.model}")
        if use_web_search:
            print(f"   🔍 Web Search: Enabled (Serper API)")
    
    def run_creative_loop(self, domain: str, initial_ideas: int = 5, 
                         max_iterations: Optional[int] = None) -> Dict[str, Any]:
        """
        Run the complete creative loop
        
        Args:
            domain: Domain to focus on (e.g., "GRC", "DevOps")
            initial_ideas: Number of ideas to generate initially
            max_iterations: Maximum iterations (uses config if None)
            
        Returns:
            Summary of the creative process
        """
        max_iter = max_iterations or config.MAX_ITERATIONS
        
        print(f"\n🎯 Starting Creative Loop")
        print(f"   Domain: {domain}")
        print(f"   Max Iterations: {max_iter}")
        print(f"   Initial Ideas: {initial_ideas}")
        print("=" * 60)
        
        # Update system state
        self._update_system_state(domain)
        
        for iteration in range(1, max_iter + 1):
            self.current_iteration = iteration
            print(f"\n🔄 ITERATION {iteration}/{max_iter}")
            print("-" * 60)
            
            # Run iteration
            iteration_result = self._run_iteration(domain, initial_ideas, iteration)
            
            # Store iteration results
            self.db.insert_iteration_result(iteration_result)
            
            # Strategist assessment
            assessment = self.strategist.execute(iteration_result)
            
            print(f"\n📊 Iteration {iteration} Summary:")
            print(f"   Ideas Generated: {len(iteration_result.generated_ideas)}")
            print(f"   Best Score: {max(e.composite_score for e in iteration_result.evaluations):.3f}")
            print(f"   Should Continue: {assessment['should_continue']}")
            print(f"   Reasoning: {assessment['reasoning'][:150]}...")
            
            # Check if we should stop
            if not assessment['should_continue']:
                print(f"\n✅ Stopping after {iteration} iterations")
                print(f"   Reason: {assessment['reasoning']}")
                self.converged = True
                break
        
        # Generate final report
        final_report = self._generate_final_report()
        
        print("\n" + "=" * 60)
        print("🏁 CREATIVE LOOP COMPLETE")
        print("=" * 60)
        print(f"Total Iterations: {self.current_iteration}")
        print(f"Total Ideas Generated: {self.total_ideas}")
        print(f"Best Score Achieved: {self.best_score:.3f}")
        
        return final_report
    
    def _run_iteration(self, domain: str, num_ideas: int, iteration: int) -> IterationResult:
        """Run a single iteration of the creative loop"""
        
        # Step 1: Generate ideas
        print("  1️⃣  Generator: Creating ideas...")
        ideas = self.generator.execute(domain=domain, num_ideas=num_ideas)
        
        # Assign IDs and iteration numbers
        for idea in ideas:
            idea.idea_id = str(uuid.uuid4())
            idea.iteration = iteration
        
        print(f"      Generated {len(ideas)} ideas")
        
        # Step 2: Compute embeddings
        print("  2️⃣  Computing embeddings...")
        embeddings = self.scoring_engine.compute_embeddings_batch(ideas)
        
        # Check for duplicates
        duplicates = self.scoring_engine.find_duplicate_ideas(ideas, embeddings)
        if duplicates:
            print(f"      ⚠️  Found {len(duplicates)} potential duplicates")
        
        # Step 3: Evaluate ideas
        print("  3️⃣  Critic: Evaluating ideas...")
        evaluations = self.critic.execute(ideas)
        
        # Enhance evaluations with semantic novelty
        for i, (idea, eval, embed) in enumerate(zip(ideas, evaluations, embeddings)):
            evaluations[i] = self.scoring_engine.enhance_evaluation_with_novelty(
                idea, eval, embed
            )
        
        print(f"      Evaluation complete")
        
        # Store ideas and evaluations in database
        for idea, evaluation, embedding in zip(ideas, evaluations, embeddings):
            self.db.insert_idea(idea)
            self.db.insert_evaluation(evaluation)
            self.db.insert_embedding(idea.idea_id, embedding)
        
        self.total_ideas += len(ideas)
        
        # Step 4: Select top ideas
        print("  4️⃣  Selecting top ideas...")
        top_ideas_with_evals = self.scoring_engine.get_top_k_diverse_ideas(
            ideas, evaluations, embeddings, k=config.TOP_K_IDEAS
        )
        top_ideas = [idea for idea, _ in top_ideas_with_evals]
        top_idea_ids = [idea.idea_id for idea in top_ideas]
        
        print(f"      Selected top {len(top_ideas)} ideas")
        for i, (idea, eval) in enumerate(top_ideas_with_evals[:3], 1):
            print(f"        {i}. {idea.idea_name} (Score: {eval.composite_score:.3f})")
        
        # Update best score
        best_eval = max(evaluations, key=lambda e: e.composite_score)
        if best_eval.composite_score > self.best_score:
            self.best_score = best_eval.composite_score
        
        # Step 5: Synthesize (merge complementary ideas)
        print("  5️⃣  Synthesizer: Merging ideas...")
        merged_ideas = self.synthesizer.execute(top_ideas, 
                                               [embeddings[ideas.index(idea)] for idea in top_ideas])
        
        if merged_ideas:
            print(f"      Created {len(merged_ideas)} synthesized ideas")
            # Store merged ideas
            for idea in merged_ideas:
                idea.idea_id = str(uuid.uuid4())
                idea.iteration = iteration
                self.db.insert_idea(idea)
                embedding = self.scoring_engine.compute_embedding(idea)
                self.db.insert_embedding(idea.idea_id, embedding)
        
        # Step 6: Disrupt (create bold variations)
        print("  6️⃣  Disruptor: Creating variations...")
        disrupted_ideas = self.disruptor.execute(top_ideas[:2])  # Disrupt top 2
        
        if disrupted_ideas:
            print(f"      Created {len(disrupted_ideas)} disrupted variations")
            # Store disrupted ideas
            for idea in disrupted_ideas:
                idea.idea_id = str(uuid.uuid4())
                idea.iteration = iteration
                self.db.insert_idea(idea)
                embedding = self.scoring_engine.compute_embedding(idea)
                self.db.insert_embedding(idea.idea_id, embedding)
        
        # Update scoring engine memory
        self.scoring_engine.update_memory(ideas, embeddings)
        
        # Create iteration result
        iteration_result = IterationResult(
            iteration_number=iteration,
            generated_ideas=ideas,
            evaluations=evaluations,
            top_ideas=top_idea_ids,
            merged_ideas=merged_ideas,
            disrupted_ideas=disrupted_ideas,
            should_continue=True,  # Will be updated by strategist
            strategist_notes=""
        )
        
        return iteration_result
    
    def _update_system_state(self, domain: Optional[str] = None):
        """Update system state in database"""
        state = {
            'current_iteration': self.current_iteration,
            'total_ideas_generated': self.total_ideas,
            'best_score': self.best_score,
            'converged': self.converged,
            'domain_focus': domain
        }
        self.db.update_system_state(state)
    
    def _generate_final_report(self) -> Dict[str, Any]:
        """Generate final report of the creative process"""
        # Get strategist report
        strategist_report = self.strategist.get_final_report()
        
        # Get top ideas from database
        top_ideas = self.db.get_top_ideas(k=10)
        
        # Export top ideas to JSON
        output_path = config.REPORTS_DIR / "top_saas_ideas.json"
        self.db.export_top_ideas_to_json(output_path, k=20)
        
        report = {
            **strategist_report,
            'output_file': str(output_path),
            'database_path': str(self.db.db_path),
            'top_ideas': top_ideas[:10]
        }
        
        # Update final system state
        self._update_system_state()
        
        return report
    
    def generate_single_batch(self, domain: str, num_ideas: int = 10) -> List[Dict[str, Any]]:
        """
        Generate and evaluate a single batch of ideas (no iteration)
        
        Args:
            domain: Domain to focus on
            num_ideas: Number of ideas to generate
            
        Returns:
            List of evaluated ideas
        """
        print(f"🎯 Generating {num_ideas} ideas in {domain} domain...")
        
        # Generate ideas
        ideas = self.generator.execute(domain=domain, num_ideas=num_ideas)
        
        # Assign IDs
        for idea in ideas:
            idea.idea_id = str(uuid.uuid4())
            idea.iteration = 0
        
        # Evaluate
        evaluations = self.critic.execute(ideas)
        
        # Compute embeddings and enhance evaluations
        embeddings = self.scoring_engine.compute_embeddings_batch(ideas)
        for i, (idea, eval, embed) in enumerate(zip(ideas, evaluations, embeddings)):
            evaluations[i] = self.scoring_engine.enhance_evaluation_with_novelty(
                idea, eval, embed
            )
            eval.calculate_composite_score(
                config.NOVELTY_WEIGHT,
                config.FEASIBILITY_WEIGHT,
                config.MARKET_FIT_WEIGHT,
                config.VIABILITY_WEIGHT
            )
        
        # Store in database
        for idea, evaluation, embedding in zip(ideas, evaluations, embeddings):
            self.db.insert_idea(idea)
            self.db.insert_evaluation(evaluation)
            self.db.insert_embedding(idea.idea_id, embedding)
        
        # Prepare results
        results = []
        for idea, eval in zip(ideas, evaluations):
            results.append({
                'idea': idea.model_dump(),
                'evaluation': {
                    'novelty': eval.novelty,
                    'feasibility': eval.feasibility,
                    'market_fit': eval.market_fit,
                    'viability': eval.viability,
                    'composite_score': eval.composite_score,
                    'justification': eval.justification
                }
            })
        
        # Sort by score
        results.sort(key=lambda x: x['evaluation']['composite_score'], reverse=True)
        
        print("✅ Generation complete!")
        print(f"Top idea: {results[0]['idea']['idea_name']} "
              f"(Score: {results[0]['evaluation']['composite_score']:.3f})")
        
        return results
    
    def close(self):
        """Clean up resources"""
        self.db.close()

