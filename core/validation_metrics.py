"""
Validation Metrics - Automated quality scoring for ideas, PRDs, and system performance
"""
import re
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
import duckdb
from core.models import SaaSIdea, Evaluation


class IdeaQualityMetrics:
    """Automated metrics for measuring idea quality"""
    
    def compute_all_metrics(self, idea: SaaSIdea) -> Dict[str, float]:
        """
        Compute all automated quality metrics for an idea
        
        Returns:
            Dictionary with individual scores and composite
        """
        specificity = self.compute_specificity(idea)
        quantification = self.compute_quantification(idea)
        differentiation = self.compute_differentiation(idea)
        feasibility = self.compute_feasibility(idea)
        completeness = self.compute_completeness(idea)
        
        # Weighted composite score
        composite = (
            specificity * 0.25 +
            quantification * 0.20 +
            differentiation * 0.25 +
            feasibility * 0.15 +
            completeness * 0.15
        )
        
        return {
            'specificity_score': round(specificity, 3),
            'quantification_score': round(quantification, 3),
            'differentiation_score': round(differentiation, 3),
            'feasibility_score': round(feasibility, 3),
            'completeness_score': round(completeness, 3),
            'composite_score': round(composite, 3)
        }
    
    def compute_specificity(self, idea: SaaSIdea) -> float:
        """
        Measure how specific the idea is (0.0 - 1.0)
        
        Checks:
        - Target user includes company size, role, and volume/scale
        - Problem statement includes time/money/risk quantification
        - Features are outcome-focused (not just technology names)
        """
        score = 0.0
        
        # Check target user specificity (0-0.4)
        target_lower = idea.target_user.lower()
        
        # Has role/title?
        has_role = any(role in target_lower for role in [
            'vp', 'vice president', 'manager', 'director', 'cto', 'cfo', 'ceo', 
            'head of', 'lead', 'analyst', 'engineer', 'operations'
        ])
        
        # Has company size?
        has_size = any(size in target_lower for size in [
            'employee', 'employees', 'person', 'people', 'user', 'users',
            '100', '500', '1000', '5000', '10000',
            'small', 'medium', 'mid-market', 'enterprise', 'startup'
        ])
        
        # Has volume/scale?
        has_volume = any(word in target_lower for word in [
            'managing', 'handling', 'processing', 'tracking', 'monitoring',
            'contracts', 'transactions', 'customers', 'vendors', 'requests',
            '50-', '100+', 'annually', 'per month', 'per year'
        ])
        
        if has_role: score += 0.15
        if has_size: score += 0.15
        if has_volume: score += 0.10
        
        # Check problem quantification (0-0.4)
        problem_lower = idea.problem_statement.lower()
        
        # Has time measurement?
        has_time = any(time in problem_lower for time in [
            'hour', 'hours', 'minute', 'minutes', 'day', 'days', 
            'week', 'weeks', 'month', 'months'
        ])
        
        # Has money measurement?
        has_money = any(money in problem_lower for money in [
            '$', 'dollar', 'dollars', 'cost', 'costs', 'spend', 'spending',
            'save', 'saving', 'savings', 'revenue', 'loss', 'waste'
        ])
        
        # Has numbers?
        has_numbers = bool(re.search(r'\d+', problem_lower))
        
        if has_time: score += 0.15
        if has_money: score += 0.15
        if has_numbers: score += 0.10
        
        # Check feature outcomes (0-0.2)
        outcome_words = [
            'reduce', 'reduces', 'reducing', 'increase', 'increases',
            'automate', 'automates', 'eliminate', 'eliminates',
            'save', 'saves', 'prevent', 'prevents', 'detect', 'detects',
            'identify', 'identifies', 'optimize', 'optimizes'
        ]
        feature_text = ' '.join(idea.core_features).lower()
        outcome_count = sum(1 for word in outcome_words if word in feature_text)
        score += min(0.2, outcome_count * 0.05)
        
        return min(1.0, score)
    
    def compute_quantification(self, idea: SaaSIdea) -> float:
        """
        Measure presence of quantified claims (0.0 - 1.0)
        
        Counts:
        - Numbers in problem statement (hours, dollars, percentages)
        - Quantified impact in features
        - Specific metrics mentioned
        """
        score = 0.0
        
        # Combine problem and features text
        text = idea.problem_statement + ' ' + ' '.join(idea.core_features)
        
        # Find dollar amounts ($50K, $10M, etc.)
        dollar_matches = re.findall(r'\$\d+[kKmMbB]?', text)
        score += min(0.3, len(dollar_matches) * 0.15)
        
        # Find time amounts (5 hours, 2 weeks, etc.)
        time_matches = re.findall(r'\d+\s*(?:hour|minute|day|week|month)', text.lower())
        score += min(0.3, len(time_matches) * 0.15)
        
        # Find percentages (85%, 50%, etc.)
        pct_matches = re.findall(r'\d+%', text)
        score += min(0.2, len(pct_matches) * 0.10)
        
        # Find other contextual numbers (500 employees, 100 contracts, etc.)
        number_context_matches = re.findall(
            r'\d+\s*(?:employee|contract|transaction|customer|vendor|request|ticket|report)',
            text.lower()
        )
        score += min(0.2, len(number_context_matches) * 0.05)
        
        return min(1.0, score)
    
    def compute_differentiation(self, idea: SaaSIdea) -> float:
        """
        Measure differentiation clarity (0.0 - 1.0)
        
        Checks:
        - Mentions competitors or alternatives ("unlike X", "compared to Y")
        - Explains "why us" not just "what we do"
        - Specific advantage (not generic "AI-powered")
        """
        score = 0.0
        diff_lower = idea.differentiator.lower()
        
        # Check for competitive comparison (0-0.4)
        comparison_words = [
            'unlike', 'compared to', 'vs', 'versus', 'instead of', 
            'rather than', 'while others', 'traditional', 'generic',
            'existing', 'competitors', 'alternatives'
        ]
        has_comparison = any(word in diff_lower for word in comparison_words)
        if has_comparison:
            score += 0.4
        
        # Check for specific advantage (0-0.3)
        generic_terms = [
            'ai-powered', 'cloud-based', 'easy to use', 'user-friendly',
            'innovative', 'best-in-class', 'cutting-edge', 'next-generation'
        ]
        
        specific_terms = [
            'automatically', 'predicts', 'learns', 'integrates with',
            'reduces by', 'increases by', 'eliminates', 'detects',
            'purpose-built', 'specifically for', 'optimized for'
        ]
        
        has_generic_only = any(term in diff_lower for term in generic_terms) and \
                          not any(term in diff_lower for term in specific_terms)
        has_specific = any(term in diff_lower for term in specific_terms)
        
        if has_specific and not has_generic_only:
            score += 0.3
        elif has_specific:
            score += 0.15
        
        # Check for "why" explanation (0-0.3)
        why_words = [
            'because', 'by', 'through', 'enables', 'allows',
            'makes possible', 'provides', 'delivers', 'achieves'
        ]
        has_why = any(word in diff_lower for word in why_words)
        if has_why:
            score += 0.3
        
        return min(1.0, score)
    
    def compute_feasibility(self, idea: SaaSIdea) -> float:
        """
        Estimate technical feasibility (0.0 - 1.0)
        
        Checks:
        - Uses proven technologies
        - Realistic scope (3-5 features for MVP)
        - No "AGI" or impossible requirements
        """
        score = 1.0  # Start at 1.0, deduct for issues
        
        # Check for unrealistic tech
        unrealistic = [
            'agi', 'general ai', 'general intelligence', 'quantum',
            'sentient', 'autonomous', 'fully automated', 'replaces humans',
            'no human input', 'perfect accuracy'
        ]
        text_lower = (idea.problem_statement + ' ' + 
                     ' '.join(idea.core_features) + ' ' + 
                     idea.differentiator).lower()
        
        for term in unrealistic:
            if term in text_lower:
                score -= 0.3
        
        # Check feature count (3-5 is ideal for MVP)
        feature_count = len(idea.core_features)
        if feature_count < 2:
            score -= 0.2  # Too vague
        elif feature_count > 7:
            score -= 0.2  # Too ambitious for MVP
        
        # Check for proven tech stack
        proven_tech = [
            'python', 'javascript', 'typescript', 'react', 'vue', 'angular',
            'node', 'postgres', 'mysql', 'mongodb', 'redis',
            'aws', 'gcp', 'azure', 'docker', 'kubernetes',
            'openai', 'anthropic', 'claude', 'gpt', 'fastapi', 'django', 'flask'
        ]
        
        highly_unproven = [
            'blockchain', 'web3', 'nft', 'metaverse', 'crypto'
        ]
        
        tech_lower = ' '.join(idea.tech_stack).lower()
        has_proven = any(tech in tech_lower for tech in proven_tech)
        has_unproven = any(tech in tech_lower for tech in highly_unproven)
        
        if has_proven:
            score += 0.1
        if has_unproven:
            score -= 0.2
        
        return max(0.0, min(1.0, score))
    
    def compute_completeness(self, idea: SaaSIdea) -> float:
        """
        Check if all required fields are populated with substance (0.0 - 1.0)
        
        Checks:
        - All fields present
        - All fields have minimum length/detail
        - No placeholder text
        """
        score = 0.0
        
        # Check field presence and length
        fields = [
            ('idea_name', idea.idea_name, 5, 0.1),
            ('problem_statement', idea.problem_statement, 50, 0.25),
            ('target_user', idea.target_user, 30, 0.2),
            ('core_features', idea.core_features, 3, 0.2),  # Min 3 features
            ('differentiator', idea.differentiator, 40, 0.15),
            ('tech_stack', idea.tech_stack, 2, 0.1)  # Min 2 technologies
        ]
        
        for field_name, value, min_threshold, weight in fields:
            if isinstance(value, str):
                if len(value.strip()) >= min_threshold:
                    score += weight
            elif isinstance(value, list):
                if len(value) >= min_threshold:
                    # Also check that list items have content
                    if all(len(str(item).strip()) > 0 for item in value):
                        score += weight
        
        return min(1.0, score)
    
    def get_score_interpretation(self, score: float) -> str:
        """Get human-readable interpretation of a score"""
        if score >= 0.8:
            return "Excellent"
        elif score >= 0.7:
            return "Good"
        elif score >= 0.6:
            return "Acceptable"
        elif score >= 0.5:
            return "Needs Improvement"
        else:
            return "Poor"


class PRDQualityMetrics:
    """Automated metrics for PRD quality"""
    
    def compute_all_metrics(self, prd: Dict[str, Any]) -> Dict[str, float]:
        """Compute all PRD quality metrics"""
        prioritization = self.compute_prioritization(prd)
        specificity = self.compute_specificity(prd)
        completeness = self.compute_completeness(prd)
        realism = self.compute_realism(prd)
        
        composite = (
            prioritization * 0.35 +
            specificity * 0.30 +
            completeness * 0.20 +
            realism * 0.15
        )
        
        return {
            'prioritization_score': round(prioritization, 3),
            'specificity_score': round(specificity, 3),
            'completeness_score': round(completeness, 3),
            'realism_score': round(realism, 3),
            'composite_score': round(composite, 3)
        }
    
    def compute_prioritization(self, prd: Dict[str, Any]) -> float:
        """
        Measure quality of feature prioritization (0.0 - 1.0)
        
        Checks:
        - P0 features are 3-4 (not 8+)
        - Each P0 has justification
        - P1/P2 clearly separated
        """
        score = 1.0
        
        mvp_features = prd.get('mvp_features', [])
        p0_features = [f for f in mvp_features if f.get('priority') == 'P0']
        p0_count = len(p0_features)
        
        # Ideal: 3-4 P0 features
        if p0_count >= 3 and p0_count <= 4:
            score = 1.0
        elif p0_count == 5:
            score = 0.8
        elif p0_count == 6:
            score = 0.6
        elif p0_count <= 2:
            score = 0.5  # Too few
        else:
            score = 0.3  # Too many (not a real MVP)
        
        # Check for P0 justifications
        if p0_count > 0:
            p0_with_justification = sum(
                1 for f in p0_features 
                if f.get('why_p0') and len(f.get('why_p0', '').strip()) > 10
            )
            justification_ratio = p0_with_justification / p0_count
            score *= justification_ratio
        
        # Check for post-MVP features (P1/P2)
        post_mvp_features = prd.get('post_mvp_features', [])
        if len(post_mvp_features) >= 3:
            score *= 1.1  # Bonus for good separation
        
        return min(1.0, score)
    
    def compute_specificity(self, prd: Dict[str, Any]) -> float:
        """Check for specific numbers, timelines, costs"""
        score = 0.0
        
        # Check roadmap has specific timelines
        roadmap = prd.get('roadmap', {})
        mvp_phase = roadmap.get('mvp_phase', {})
        timeline_text = str(mvp_phase.get('timeline', '')).lower()
        
        if 'month' in timeline_text or 'week' in timeline_text:
            # Check if it has a number
            if re.search(r'\d+', timeline_text):
                score += 0.3
        
        # Check pricing has specific numbers
        pricing_tiers = prd.get('business_model', {}).get('pricing_tiers', [])
        tiers_with_price = sum(1 for tier in pricing_tiers if '$' in str(tier.get('price', '')))
        if tiers_with_price >= 2:
            score += 0.3
        elif tiers_with_price >= 1:
            score += 0.15
        
        # Check for quantified success metrics
        success_metrics = prd.get('executive_summary', {}).get('success_metrics', [])
        metrics_with_numbers = sum(1 for metric in success_metrics if re.search(r'\d+', str(metric)))
        score += min(0.4, metrics_with_numbers * 0.13)
        
        return min(1.0, score)
    
    def compute_completeness(self, prd: Dict[str, Any]) -> float:
        """Check all required sections are present"""
        score = 0.0
        
        required_sections = [
            'product_name',
            'tagline',
            'executive_summary',
            'problem_and_solution',
            'target_users',
            'mvp_features',
            'technical_architecture',
            'business_model',
            'go_to_market',
            'roadmap'
        ]
        
        for section in required_sections:
            if section in prd and prd[section]:
                score += 1.0 / len(required_sections)
        
        return score
    
    def compute_realism(self, prd: Dict[str, Any]) -> float:
        """Assess if timelines and scope are realistic"""
        score = 1.0
        
        # Check MVP timeline
        roadmap = prd.get('roadmap', {})
        mvp_phase = roadmap.get('mvp_phase', {})
        timeline_text = str(mvp_phase.get('timeline', '')).lower()
        
        # Extract months
        months_match = re.search(r'(\d+)\s*month', timeline_text)
        if months_match:
            months = int(months_match.group(1))
            
            # Check against P0 feature count
            mvp_features = prd.get('mvp_features', [])
            p0_count = sum(1 for f in mvp_features if f.get('priority') == 'P0')
            
            # Rule of thumb: 1-2 months per P0 feature
            expected_months = p0_count * 1.5
            
            if months < expected_months * 0.5:
                score -= 0.3  # Too optimistic
            elif months > expected_months * 2:
                score -= 0.2  # Too conservative (but less bad)
        
        return max(0.0, score)


class PromptPerformanceTracker:
    """Track performance of different prompt versions over time"""
    
    def __init__(self, db_path: str = "data/prompt_performance.duckdb"):
        self.db_path = db_path
        self.conn = duckdb.connect(db_path)
        self._initialize_db()
    
    def _initialize_db(self):
        """Create tables for tracking if they don't exist"""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS prompt_runs (
                run_id VARCHAR PRIMARY KEY,
                agent_name VARCHAR,
                prompt_version VARCHAR,
                timestamp TIMESTAMP,
                domain VARCHAR,
                num_ideas INTEGER,
                prompt_text TEXT
            )
        """)
        
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS idea_metrics (
                run_id VARCHAR,
                idea_id VARCHAR,
                idea_name VARCHAR,
                specificity_score FLOAT,
                quantification_score FLOAT,
                differentiation_score FLOAT,
                feasibility_score FLOAT,
                completeness_score FLOAT,
                auto_composite_score FLOAT,
                critic_novelty FLOAT,
                critic_feasibility FLOAT,
                critic_market_fit FLOAT,
                critic_viability FLOAT,
                critic_composite_score FLOAT,
                PRIMARY KEY (run_id, idea_id)
            )
        """)
        
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS prd_metrics (
                run_id VARCHAR PRIMARY KEY,
                idea_id VARCHAR,
                prioritization_score FLOAT,
                specificity_score FLOAT,
                completeness_score FLOAT,
                realism_score FLOAT,
                composite_score FLOAT
            )
        """)
    
    def log_run(
        self,
        agent_name: str,
        prompt_version: str,
        ideas: List[SaaSIdea],
        evaluations: Optional[List[Evaluation]] = None,
        prompt_text: Optional[str] = None
    ) -> str:
        """
        Log a prompt run with automated metrics
        
        Returns:
            run_id for this run
        """
        run_id = str(uuid.uuid4())
        
        # Log run metadata
        self.conn.execute("""
            INSERT INTO prompt_runs VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            run_id,
            agent_name,
            prompt_version,
            datetime.now(),
            ideas[0].domain.value if ideas and hasattr(ideas[0].domain, 'value') else str(ideas[0].domain) if ideas else None,
            len(ideas),
            prompt_text[:1000] if prompt_text else None  # Truncate for storage
        ))
        
        # Compute and log metrics for each idea
        metrics_calculator = IdeaQualityMetrics()
        
        for i, idea in enumerate(ideas):
            auto_metrics = metrics_calculator.compute_all_metrics(idea)
            
            # Get critic metrics if available
            evaluation = evaluations[i] if evaluations and i < len(evaluations) else None
            
            self.conn.execute("""
                INSERT INTO idea_metrics VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                run_id,
                idea.idea_id,
                idea.idea_name,
                auto_metrics['specificity_score'],
                auto_metrics['quantification_score'],
                auto_metrics['differentiation_score'],
                auto_metrics['feasibility_score'],
                auto_metrics['completeness_score'],
                auto_metrics['composite_score'],
                evaluation.novelty if evaluation else None,
                evaluation.feasibility if evaluation else None,
                evaluation.market_fit if evaluation else None,
                evaluation.viability if evaluation else None,
                evaluation.composite_score if evaluation else None
            ))
        
        return run_id
    
    def get_run_summary(self, run_id: str) -> Dict[str, Any]:
        """Get summary metrics for a specific run"""
        result = self.conn.execute("""
            SELECT 
                COUNT(*) as num_ideas,
                AVG(specificity_score) as avg_specificity,
                AVG(quantification_score) as avg_quantification,
                AVG(differentiation_score) as avg_differentiation,
                AVG(feasibility_score) as avg_feasibility,
                AVG(completeness_score) as avg_completeness,
                AVG(auto_composite_score) as avg_auto_composite,
                AVG(critic_composite_score) as avg_critic_composite
            FROM idea_metrics
            WHERE run_id = ?
        """, (run_id,)).fetchone()
        
        if result:
            return {
                'num_ideas': result[0],
                'avg_specificity': round(result[1], 3) if result[1] else None,
                'avg_quantification': round(result[2], 3) if result[2] else None,
                'avg_differentiation': round(result[3], 3) if result[3] else None,
                'avg_feasibility': round(result[4], 3) if result[4] else None,
                'avg_completeness': round(result[5], 3) if result[5] else None,
                'avg_auto_composite': round(result[6], 3) if result[6] else None,
                'avg_critic_composite': round(result[7], 3) if result[7] else None
            }
        return {}
    
    def compare_prompt_versions(self, version_a: str, version_b: str, agent_name: str) -> Dict[str, Any]:
        """
        Compare two prompt versions statistically
        
        Returns:
            Comparison results with statistical significance
        """
        # Get aggregate stats for each version
        query = """
            SELECT 
                pr.prompt_version,
                COUNT(DISTINCT pr.run_id) as num_runs,
                COUNT(*) as num_ideas,
                AVG(im.specificity_score) as avg_specificity,
                AVG(im.quantification_score) as avg_quantification,
                AVG(im.differentiation_score) as avg_differentiation,
                AVG(im.auto_composite_score) as avg_auto_composite,
                AVG(im.critic_composite_score) as avg_critic_composite,
                STDDEV(im.auto_composite_score) as std_auto_composite
            FROM prompt_runs pr
            JOIN idea_metrics im ON pr.run_id = im.run_id
            WHERE pr.agent_name = ?
              AND pr.prompt_version IN (?, ?)
            GROUP BY pr.prompt_version
        """
        
        comparison = self.conn.execute(query, (agent_name, version_a, version_b)).fetchdf()
        
        if len(comparison) < 2:
            return {
                'error': 'Insufficient data for comparison',
                'versions_found': len(comparison)
            }
        
        # Get individual scores for statistical test
        version_a_scores = self.conn.execute("""
            SELECT im.auto_composite_score
            FROM prompt_runs pr
            JOIN idea_metrics im ON pr.run_id = im.run_id
            WHERE pr.agent_name = ? AND pr.prompt_version = ?
              AND im.auto_composite_score IS NOT NULL
        """, (agent_name, version_a)).fetchall()
        
        version_b_scores = self.conn.execute("""
            SELECT im.auto_composite_score
            FROM prompt_runs pr
            JOIN idea_metrics im ON pr.run_id = im.run_id
            WHERE pr.agent_name = ? AND pr.prompt_version = ?
              AND im.auto_composite_score IS NOT NULL
        """, (agent_name, version_b)).fetchall()
        
        # Perform t-test if we have enough data
        p_value = None
        significant = False
        
        if len(version_a_scores) >= 3 and len(version_b_scores) >= 3:
            try:
                from scipy import stats
                scores_a = [s[0] for s in version_a_scores]
                scores_b = [s[0] for s in version_b_scores]
                t_stat, p_value = stats.ttest_ind(scores_a, scores_b)
                significant = p_value < 0.05
            except ImportError:
                pass  # scipy not available
        
        return {
            'comparison_table': comparison,
            'p_value': p_value,
            'statistically_significant': significant,
            'version_a_scores': len(version_a_scores),
            'version_b_scores': len(version_b_scores)
        }
    
    def get_agent_history(self, agent_name: str, limit: int = 20) -> Dict[str, Any]:
        """Get recent performance history for an agent"""
        history = self.conn.execute("""
            SELECT 
                pr.run_id,
                pr.prompt_version,
                pr.timestamp,
                pr.num_ideas,
                AVG(im.auto_composite_score) as avg_score
            FROM prompt_runs pr
            LEFT JOIN idea_metrics im ON pr.run_id = im.run_id
            WHERE pr.agent_name = ?
            GROUP BY pr.run_id, pr.prompt_version, pr.timestamp, pr.num_ideas
            ORDER BY pr.timestamp DESC
            LIMIT ?
        """, (agent_name, limit)).fetchdf()
        
        return {
            'agent_name': agent_name,
            'recent_runs': history.to_dict('records') if not history.empty else []
        }
    
    def close(self):
        """Close database connection"""
        self.conn.close()

