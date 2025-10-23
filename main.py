"""
Main entry point for the Multi-Agent Creativity System
"""
import argparse
import json
import os
import sys
from pathlib import Path

from config import config
from core.orchestrator import CreativityOrchestrator
from core.models import Domain
from core.web_search import get_search_engine
from agents.base_agent import BaseAgent
from core.validation_metrics import IdeaQualityMetrics, PromptPerformanceTracker


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Multi-Agent Creativity System for SaaS Product Ideation"
    )
    
    parser.add_argument(
        'command',
        choices=['generate', 'creative-loop', 'export'],
        help='Command to execute'
    )
    
    parser.add_argument(
        '--domain',
        type=str,
        choices=[d.value for d in Domain],
        default=Domain.CLOUD.value,
        help='Domain to focus on for ideation'
    )
    
    parser.add_argument(
        '--prompt',
        type=str,
        default=None,
        help='Custom prompt for ideation (overrides --domain if provided)'
    )
    
    parser.add_argument(
        '--use-search',
        action='store_true',
        help='Enable web search for market intelligence (requires SERPER_API_KEY)'
    )
    
    parser.add_argument(
        '--num-ideas',
        type=int,
        default=5,
        help='Number of ideas to generate per iteration'
    )
    
    parser.add_argument(
        '--max-iterations',
        type=int,
        default=None,
        help='Maximum number of iterations (default: from config)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='Output file path for results'
    )
    
    args = parser.parse_args()
    
    # Check for API keys or AWS Bedrock access
    if config.USE_AWS_BEDROCK:
        print(f"✅ Using AWS Bedrock with profile: {config.AWS_PROFILE}")
        print(f"   Region: {config.AWS_REGION}")
        # Skip validation if using environment credentials or in ECS
        in_ecs = os.getenv('AWS_EXECUTION_ENV') or os.getenv('ECS_CONTAINER_METADATA_URI')
        if os.getenv('AWS_ACCESS_KEY_ID'):
            print(f"   Using AWS credentials from environment variables")
        elif in_ecs:
            print(f"   Using ECS task IAM role (validation skipped)")
        elif config.AWS_PROFILE and config.AWS_PROFILE.strip():
            # Only validate if using a profile locally
            try:
                import boto3
                session = boto3.Session(profile_name=config.AWS_PROFILE)
                session.client('bedrock-runtime', region_name=config.AWS_REGION)
                print(f"   AWS profile validated successfully")
            except Exception as e:
                print(f"❌ Error: Cannot access AWS Bedrock with profile '{config.AWS_PROFILE}'")
                print(f"   Error: {str(e)}")
                print(f"   Please ensure AWS CLI is configured with the '{config.AWS_PROFILE}' profile")
                sys.exit(1)
        else:
            print(f"   Warning: No credentials detected. Proceeding anyway...")
    elif not config.ANTHROPIC_API_KEY and not config.OPENAI_API_KEY:
        print("❌ Error: No API access configured!")
        print("   Option 1: Use AWS Bedrock (default)")
        print("     - Set USE_AWS_BEDROCK=true in .env")
        print("     - Configure AWS CLI with 'diligent' profile")
        print("   Option 2: Use Anthropic API directly")
        print("     - Set USE_AWS_BEDROCK=false in .env")
        print("     - Set ANTHROPIC_API_KEY in .env")
        sys.exit(1)
    
    # Check for web search requirements
    if args.use_search and not config.SERPER_API_KEY:
        print("⚠️  Warning: --use-search enabled but SERPER_API_KEY not found in .env")
        print("   Web search will be disabled. Please add SERPER_API_KEY to use this feature.")
        args.use_search = False
    
    # Initialize orchestrator with web search if enabled
    orchestrator = CreativityOrchestrator(use_web_search=args.use_search)
    
    try:
        if args.command == 'generate':
            # Generate a single batch of ideas
            # Use custom prompt if provided, otherwise use domain
            ideation_focus = args.prompt if args.prompt else args.domain
            
            if args.prompt:
                print(f"\n🚀 Generating {args.num_ideas} SaaS ideas")
                print(f"   Custom Prompt: \"{args.prompt}\"\n")
            else:
                print(f"\n🚀 Generating {args.num_ideas} SaaS ideas in {args.domain} domain\n")
            
            results = orchestrator.generate_single_batch(
                domain=ideation_focus,
                num_ideas=args.num_ideas
            )
            
            # Display results
            print("\n" + "=" * 80)
            print("📋 GENERATED IDEAS")
            print("=" * 80)
            
            # Compute automatic quality metrics
            metrics_calculator = IdeaQualityMetrics()
            all_auto_scores = []
            all_critic_scores = []
            
            for i, result in enumerate(results[:5], 1):
                idea = result['idea']
                eval = result['evaluation']
                
                # Compute automated quality metrics
                from core.models import SaaSIdea
                idea_obj = SaaSIdea(
                    idea_name=idea['idea_name'],
                    problem_statement=idea['problem_statement'],
                    target_user=idea['target_user'],
                    core_features=idea['core_features'],
                    differentiator=idea['differentiator'],
                    tech_stack=idea.get('tech_stack', []),
                    revenue_model=idea.get('revenue_model', 'Subscription'),
                    domain=idea.get('domain', Domain.CLOUD)
                )
                auto_metrics = metrics_calculator.compute_all_metrics(idea_obj)
                all_auto_scores.append(auto_metrics['composite_score'])
                all_critic_scores.append(eval['composite_score'])
                
                print(f"\n{i}. {idea['idea_name']}")
                print(f"   Critic Score: {eval['composite_score']:.3f} "
                      f"(N:{eval['novelty']:.2f} F:{eval['feasibility']:.2f} "
                      f"M:{eval['market_fit']:.2f} V:{eval['viability']:.2f})")
                print(f"   Auto Metrics: {auto_metrics['composite_score']:.3f} "
                      f"(Spec:{auto_metrics['specificity_score']:.2f} Quant:{auto_metrics['quantification_score']:.2f} "
                      f"Diff:{auto_metrics['differentiation_score']:.2f})")
                print(f"   Problem: {idea['problem_statement'][:100]}...")
                print(f"   Target: {idea['target_user']}")
                print(f"   Differentiator: {idea['differentiator'][:80]}...")
            
            # Display aggregate quality metrics
            if all_auto_scores:
                avg_auto = sum(all_auto_scores) / len(all_auto_scores)
                avg_critic = sum(all_critic_scores) / len(all_critic_scores)
                
                print(f"\n" + "=" * 80)
                print("📊 QUALITY METRICS SUMMARY")
                print("=" * 80)
                print(f"Average Automated Quality Score: {avg_auto:.3f} "
                      f"({metrics_calculator.get_score_interpretation(avg_auto)})")
                print(f"Average Critic Score: {avg_critic:.3f} "
                      f"({metrics_calculator.get_score_interpretation(avg_critic)})")
                print(f"Ideas Shown: {len(all_auto_scores)} of {len(results)}")
                
                # Quality interpretation guide
                print(f"\n📈 Score Interpretation:")
                print(f"   • 0.8+ = Excellent (production-ready)")
                print(f"   • 0.7-0.8 = Good (minor refinements)")
                print(f"   • 0.6-0.7 = Acceptable (needs improvement)")
                print(f"   • < 0.6 = Needs significant work")
            
            # Save results
            if args.output:
                output_path = args.output
            elif args.prompt:
                # Create safe filename from prompt
                safe_prompt = "".join(c if c.isalnum() or c in (' ', '_') else '_' for c in args.prompt)[:50]
                output_path = config.REPORTS_DIR / f"batch_results_{safe_prompt.replace(' ', '_').lower()}.json"
            else:
                output_path = config.REPORTS_DIR / f"batch_results_{args.domain.lower()}.json"
            
            with open(output_path, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            
            print(f"\n💾 Full results saved to: {output_path}")
            
            # Show error recovery statistics
            from core.error_recovery import get_error_recovery_engine
            stats = get_error_recovery_engine().get_error_statistics()
            if stats and stats['total_recovery_attempts'] > 0:
                print(f"\n🔧 Error Recovery Statistics:")
                print(f"   Recovery Attempts: {stats['total_recovery_attempts']}")
                print(f"   Successful: {stats['successful_recoveries']}")
                print(f"   Success Rate: {stats['recovery_success_rate']*100:.1f}%")
            
            # Show LLM cost statistics
            llm_cost = BaseAgent.get_cost_summary()
            if llm_cost['total_api_calls'] > 0:
                print(f"\n💰 LLM Cost Statistics:")
                print(f"   Model: {llm_cost['model']}")
                print(f"   API Calls: {llm_cost['total_api_calls']}")
                print(f"   Input Tokens: {llm_cost['total_input_tokens']:,}")
                print(f"   Output Tokens: {llm_cost['total_output_tokens']:,}")
                print(f"   Total Tokens: {llm_cost['total_tokens']:,}")
                print(f"   Input Cost: ${llm_cost['input_cost_usd']:.4f}")
                print(f"   Output Cost: ${llm_cost['output_cost_usd']:.4f}")
                print(f"   Total LLM Cost: ${llm_cost['total_cost_usd']:.4f}")
            
            # Show web search cost statistics
            if args.use_search and config.SERPER_API_KEY:
                try:
                    search_engine = get_search_engine()
                    cost_summary = search_engine.get_cost_summary(assume_free_tier=True)
                    if cost_summary['total_searches'] > 0:
                        print(f"\n🔍 Web Search Statistics:")
                        print(f"   Total Searches: {cost_summary['total_searches']}")
                        print(f"   Cost: ${cost_summary['cost_usd']:.3f} (Free Tier)")
                        if not cost_summary['within_free_tier']:
                            paid_cost = search_engine.get_search_cost(assume_free_tier=False)
                            print(f"   ⚠️  Exceeded free tier limit ({cost_summary['free_tier_limit']} searches/month)")
                            print(f"   Paid Tier Cost: ${paid_cost:.3f}")
                        else:
                            remaining = cost_summary['free_tier_limit'] - cost_summary['total_searches']
                            print(f"   Remaining Free: {remaining} searches this month")
                        
                        # Show combined cost
                        total_cost = llm_cost['total_cost_usd'] + cost_summary['cost_usd']
                        print(f"\n💵 Total Session Cost: ${total_cost:.4f}")
                except Exception:
                    # If search engine not initialized, just show LLM cost
                    if llm_cost['total_api_calls'] > 0:
                        print(f"\n💵 Total Session Cost: ${llm_cost['total_cost_usd']:.4f} (LLM only)")
            else:
                # No web search, just LLM cost
                if llm_cost['total_api_calls'] > 0:
                    print(f"\n💵 Total Session Cost: ${llm_cost['total_cost_usd']:.4f}")
        
        elif args.command == 'creative-loop':
            # Run full creative loop
            # Use custom prompt if provided, otherwise use domain
            ideation_focus = args.prompt if args.prompt else args.domain
            
            if args.prompt:
                print(f"\n🔄 Starting Multi-Agent Creative Loop")
                print(f"   Custom Prompt: \"{args.prompt}\"\n")
            else:
                print(f"\n🔄 Starting Multi-Agent Creative Loop")
                print(f"   Domain: {args.domain}\n")
            
            report = orchestrator.run_creative_loop(
                domain=ideation_focus,
                initial_ideas=args.num_ideas,
                max_iterations=args.max_iterations
            )
            
            # Display final report
            print("\n" + "=" * 80)
            print("📊 FINAL REPORT")
            print("=" * 80)
            print(f"Total Iterations: {report['total_iterations']}")
            print(f"Total Ideas: {report['total_ideas_generated']}")
            print(f"Best Score: {report['best_score']:.3f}")
            print(f"Average Score: {report['average_score']:.3f}")
            print(f"\n📈 Score Progression:")
            for i, score in enumerate(report['score_progression'], 1):
                bar = "█" * int(score * 50)
                print(f"   Iteration {i:2d}: {bar} {score:.3f}")
            
            print(f"\n💾 Results saved to: {report['output_file']}")
            # print(f"💾 Database: {report['database_path']}")
            
            # Show error recovery statistics
            from core.error_recovery import get_error_recovery_engine
            stats = get_error_recovery_engine().get_error_statistics()
            if stats and stats['total_recovery_attempts'] > 0:
                print(f"\n🔧 Error Recovery Statistics:")
                print(f"   Recovery Attempts: {stats['total_recovery_attempts']}")
                print(f"   Successful: {stats['successful_recoveries']}")
                print(f"   Success Rate: {stats['recovery_success_rate']*100:.1f}%")
                
                # Save error patterns
                error_report_path = config.REPORTS_DIR / "error_recovery_patterns.json"
                get_error_recovery_engine().save_error_patterns(str(error_report_path))
                print(f"   📊 Error patterns saved to: {error_report_path}")
            
            # Show LLM cost statistics
            llm_cost = BaseAgent.get_cost_summary()
            if llm_cost['total_api_calls'] > 0:
                print(f"\n💰 LLM Cost Statistics:")
                print(f"   Model: {llm_cost['model']}")
                print(f"   API Calls: {llm_cost['total_api_calls']}")
                print(f"   Input Tokens: {llm_cost['total_input_tokens']:,}")
                print(f"   Output Tokens: {llm_cost['total_output_tokens']:,}")
                print(f"   Total Tokens: {llm_cost['total_tokens']:,}")
                print(f"   Input Cost: ${llm_cost['input_cost_usd']:.4f}")
                print(f"   Output Cost: ${llm_cost['output_cost_usd']:.4f}")
                print(f"   Total LLM Cost: ${llm_cost['total_cost_usd']:.4f}")
            
            # Show web search cost statistics
            if args.use_search and config.SERPER_API_KEY:
                try:
                    search_engine = get_search_engine()
                    cost_summary = search_engine.get_cost_summary(assume_free_tier=True)
                    if cost_summary['total_searches'] > 0:
                        print(f"\n🔍 Web Search Statistics:")
                        print(f"   Total Searches: {cost_summary['total_searches']}")
                        print(f"   Cost: ${cost_summary['cost_usd']:.3f} (Free Tier)")
                        if not cost_summary['within_free_tier']:
                            paid_cost = search_engine.get_search_cost(assume_free_tier=False)
                            print(f"   ⚠️  Exceeded free tier limit ({cost_summary['free_tier_limit']} searches/month)")
                            print(f"   Paid Tier Cost: ${paid_cost:.3f}")
                        else:
                            remaining = cost_summary['free_tier_limit'] - cost_summary['total_searches']
                            print(f"   Remaining Free: {remaining} searches this month")
                        
                        # Show combined cost
                        total_cost = llm_cost['total_cost_usd'] + cost_summary['cost_usd']
                        print(f"\n💵 Total Session Cost: ${total_cost:.4f}")
                except Exception:
                    # If search engine not initialized, just show LLM cost
                    if llm_cost['total_api_calls'] > 0:
                        print(f"\n💵 Total Session Cost: ${llm_cost['total_cost_usd']:.4f} (LLM only)")
            else:
                # No web search, just LLM cost
                if llm_cost['total_api_calls'] > 0:
                    print(f"\n💵 Total Session Cost: ${llm_cost['total_cost_usd']:.4f}")
        
        elif args.command == 'export':
            # Export top ideas
            output_path = args.output or config.REPORTS_DIR / "exported_ideas.json"
            orchestrator.db.export_top_ideas_to_json(output_path, k=20)
            print(f"✅ Exported top 20 ideas to: {output_path}")
    
    finally:
        orchestrator.close()


if __name__ == "__main__":
    main()

