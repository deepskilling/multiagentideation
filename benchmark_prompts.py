"""
Benchmark script to measure and compare prompt performance
"""
import argparse
import json
from datetime import datetime
from typing import List, Optional

from config import config
from core.models import Domain, SaaSIdea, Evaluation
from core.validation_metrics import IdeaQualityMetrics, PromptPerformanceTracker
from agents.generator_agent import GeneratorAgent
from agents.critic_agent import CriticAgent


def run_benchmark(
    domain: str,
    num_ideas: int = 5,
    num_runs: int = 3,
    prompt_version: str = "current",
    verbose: bool = False
) -> dict:
    """
    Run a benchmark test for idea generation quality
    
    Args:
        domain: Domain or prompt to test
        num_ideas: Number of ideas to generate per run
        num_runs: Number of times to repeat the test
        prompt_version: Version identifier for this prompt
        verbose: Print detailed output
        
    Returns:
        Dictionary with aggregate results
    """
    print(f"\n{'=' * 80}")
    print(f"🎯 BENCHMARK TEST: {domain}")
    print(f"{'=' * 80}")
    print(f"Configuration:")
    print(f"  • Domain/Prompt: {domain}")
    print(f"  • Ideas per run: {num_ideas}")
    print(f"  • Number of runs: {num_runs}")
    print(f"  • Prompt version: {prompt_version}")
    print(f"  • Model: Claude Sonnet 4.5 (AWS Bedrock)")
    print(f"  • Temperature: 0.7")
    print(f"\n{'=' * 80}\n")
    
    # Initialize agents and metrics
    generator = GeneratorAgent()
    critic = CriticAgent()
    metrics_calculator = IdeaQualityMetrics()
    tracker = PromptPerformanceTracker()
    
    all_runs_results = []
    
    for run_num in range(1, num_runs + 1):
        print(f"\n🔄 Run {run_num}/{num_runs}")
        print(f"{'-' * 80}")
        
        # Generate ideas
        ideas = generator.execute(
            domain=domain,
            context="",
            num_ideas=num_ideas
        )
        
        # Evaluate ideas
        evaluations = critic.execute(ideas, use_search=False)
        
        # Compute automated metrics
        run_scores = {
            'auto_scores': [],
            'critic_scores': [],
            'ideas': []
        }
        
        for i, (idea, evaluation) in enumerate(zip(ideas, evaluations), 1):
            auto_metrics = metrics_calculator.compute_all_metrics(idea)
            
            run_scores['auto_scores'].append(auto_metrics['composite_score'])
            run_scores['critic_scores'].append(evaluation.composite_score)
            run_scores['ideas'].append({
                'name': idea.idea_name,
                'auto_metrics': auto_metrics,
                'critic_scores': {
                    'composite': evaluation.composite_score,
                    'novelty': evaluation.novelty,
                    'feasibility': evaluation.feasibility,
                    'market_fit': evaluation.market_fit,
                    'viability': evaluation.viability
                }
            })
            
            if verbose:
                print(f"\n  {i}. {idea.idea_name}")
                print(f"     Auto: {auto_metrics['composite_score']:.3f} | "
                      f"Critic: {evaluation.composite_score:.3f}")
        
        # Log to performance tracker
        run_id = tracker.log_run(
            agent_name="GeneratorAgent",
            prompt_version=prompt_version,
            ideas=ideas,
            evaluations=evaluations
        )
        
        # Calculate run statistics
        avg_auto = sum(run_scores['auto_scores']) / len(run_scores['auto_scores'])
        avg_critic = sum(run_scores['critic_scores']) / len(run_scores['critic_scores'])
        
        print(f"\n  Run {run_num} Summary:")
        print(f"    Avg Auto Score: {avg_auto:.3f} "
              f"({metrics_calculator.get_score_interpretation(avg_auto)})")
        print(f"    Avg Critic Score: {avg_critic:.3f} "
              f"({metrics_calculator.get_score_interpretation(avg_critic)})")
        
        all_runs_results.append({
            'run_id': run_id,
            'run_num': run_num,
            'avg_auto_score': avg_auto,
            'avg_critic_score': avg_critic,
            'ideas': run_scores['ideas']
        })
    
    # Aggregate across all runs
    all_auto_scores = [r['avg_auto_score'] for r in all_runs_results]
    all_critic_scores = [r['avg_critic_score'] for r in all_runs_results]
    
    avg_auto_overall = sum(all_auto_scores) / len(all_auto_scores)
    avg_critic_overall = sum(all_critic_scores) / len(all_critic_scores)
    
    # Calculate standard deviation for consistency
    import math
    if len(all_auto_scores) > 1:
        auto_variance = sum((x - avg_auto_overall) ** 2 for x in all_auto_scores) / (len(all_auto_scores) - 1)
        auto_std = math.sqrt(auto_variance)
    else:
        auto_std = 0.0
    
    if len(all_critic_scores) > 1:
        critic_variance = sum((x - avg_critic_overall) ** 2 for x in all_critic_scores) / (len(all_critic_scores) - 1)
        critic_std = math.sqrt(critic_variance)
    else:
        critic_std = 0.0
    
    # Display final results
    print(f"\n{'=' * 80}")
    print(f"📊 BENCHMARK RESULTS")
    print(f"{'=' * 80}")
    print(f"\n🎯 Overall Performance ({num_runs} runs, {num_ideas * num_runs} total ideas):")
    print(f"  • Avg Auto Score: {avg_auto_overall:.3f} ± {auto_std:.3f} "
          f"({metrics_calculator.get_score_interpretation(avg_auto_overall)})")
    print(f"  • Avg Critic Score: {avg_critic_overall:.3f} ± {critic_std:.3f} "
          f"({metrics_calculator.get_score_interpretation(avg_critic_overall)})")
    
    consistency_rating = "High" if auto_std < 0.05 else "Medium" if auto_std < 0.10 else "Low"
    print(f"\n📉 Consistency: {consistency_rating} (σ = {auto_std:.3f})")
    
    # Show quality breakdown
    print(f"\n📈 Quality Breakdown (averaged across all ideas):")
    
    # Calculate component averages
    all_specificity = []
    all_quantification = []
    all_differentiation = []
    all_feasibility = []
    all_completeness = []
    
    for run in all_runs_results:
        for idea_data in run['ideas']:
            all_specificity.append(idea_data['auto_metrics']['specificity_score'])
            all_quantification.append(idea_data['auto_metrics']['quantification_score'])
            all_differentiation.append(idea_data['auto_metrics']['differentiation_score'])
            all_feasibility.append(idea_data['auto_metrics']['feasibility_score'])
            all_completeness.append(idea_data['auto_metrics']['completeness_score'])
    
    print(f"  • Specificity: {sum(all_specificity) / len(all_specificity):.3f}")
    print(f"  • Quantification: {sum(all_quantification) / len(all_quantification):.3f}")
    print(f"  • Differentiation: {sum(all_differentiation) / len(all_differentiation):.3f}")
    print(f"  • Feasibility: {sum(all_feasibility) / len(all_feasibility):.3f}")
    print(f"  • Completeness: {sum(all_completeness) / len(all_completeness):.3f}")
    
    # Save detailed results
    output_file = config.REPORTS_DIR / f"benchmark_{prompt_version}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    output_data = {
        'benchmark_config': {
            'domain': domain,
            'num_ideas': num_ideas,
            'num_runs': num_runs,
            'prompt_version': prompt_version,
            'model': 'Claude Sonnet 4.5 (AWS Bedrock)',
            'temperature': 0.7,
            'timestamp': datetime.now().isoformat()
        },
        'results': {
            'avg_auto_score': avg_auto_overall,
            'auto_std': auto_std,
            'avg_critic_score': avg_critic_overall,
            'critic_std': critic_std,
            'consistency_rating': consistency_rating
        },
        'component_scores': {
            'specificity': sum(all_specificity) / len(all_specificity),
            'quantification': sum(all_quantification) / len(all_quantification),
            'differentiation': sum(all_differentiation) / len(all_differentiation),
            'feasibility': sum(all_feasibility) / len(all_feasibility),
            'completeness': sum(all_completeness) / len(all_completeness)
        },
        'runs': all_runs_results
    }
    
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2, default=str)
    
    print(f"\n💾 Detailed results saved to: {output_file}")
    print(f"{'=' * 80}\n")
    
    tracker.close()
    
    return output_data


def compare_benchmarks(version_a: str, version_b: str):
    """Compare two benchmark versions from the database"""
    tracker = PromptPerformanceTracker()
    
    print(f"\n{'=' * 80}")
    print(f"🔬 COMPARING PROMPT VERSIONS")
    print(f"{'=' * 80}")
    print(f"Version A: {version_a}")
    print(f"Version B: {version_b}\n")
    
    comparison = tracker.compare_prompt_versions(version_a, version_b, "GeneratorAgent")
    
    if 'error' in comparison:
        print(f"❌ {comparison['error']}")
        print(f"   Versions found: {comparison.get('versions_found', 0)}")
        print(f"\nTip: Run benchmarks for both versions first:")
        print(f"  python benchmark_prompts.py --version {version_a} --domain 'your domain'")
        print(f"  python benchmark_prompts.py --version {version_b} --domain 'your domain'")
        tracker.close()
        return
    
    # Display comparison table
    df = comparison['comparison_table']
    print("📊 Comparison Results:\n")
    print(df.to_string(index=False))
    
    # Statistical significance
    if comparison['p_value'] is not None:
        print(f"\n📈 Statistical Analysis:")
        print(f"  • p-value: {comparison['p_value']:.4f}")
        print(f"  • Statistically significant: {'✅ Yes' if comparison['statistically_significant'] else '❌ No'}")
        print(f"  • Sample sizes: {comparison['version_a_scores']} vs {comparison['version_b_scores']} ideas")
        
        if comparison['statistically_significant']:
            print(f"\n🎉 The difference is statistically significant (p < 0.05)!")
        else:
            print(f"\n⚠️  The difference is not statistically significant.")
            print(f"   Consider running more benchmark iterations for conclusive results.")
    
    print(f"{'=' * 80}\n")
    
    tracker.close()


def main():
    parser = argparse.ArgumentParser(
        description="Benchmark prompt performance with automated quality metrics"
    )
    
    parser.add_argument(
        '--domain',
        type=str,
        default="GRC compliance software",
        help='Domain or prompt to test'
    )
    
    parser.add_argument(
        '--num-ideas',
        type=int,
        default=5,
        help='Number of ideas to generate per run'
    )
    
    parser.add_argument(
        '--num-runs',
        type=int,
        default=3,
        help='Number of runs to perform for statistical significance'
    )
    
    parser.add_argument(
        '--version',
        type=str,
        default="current",
        help='Prompt version identifier (e.g., "v1_baseline", "v2_few_shot")'
    )
    
    parser.add_argument(
        '--compare',
        nargs=2,
        metavar=('VERSION_A', 'VERSION_B'),
        help='Compare two existing benchmark versions'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Print detailed output for each idea'
    )
    
    args = parser.parse_args()
    
    if args.compare:
        compare_benchmarks(args.compare[0], args.compare[1])
    else:
        run_benchmark(
            domain=args.domain,
            num_ideas=args.num_ideas,
            num_runs=args.num_runs,
            prompt_version=args.version,
            verbose=args.verbose
        )


if __name__ == '__main__':
    main()

