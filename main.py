"""
Main entry point for the Multi-Agent Creativity System
"""
import argparse
import json
import sys
from pathlib import Path

from config import config
from core.orchestrator import CreativityOrchestrator
from core.models import Domain


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
        # Verify AWS credentials are available
        try:
            import boto3
            session = boto3.Session(profile_name=config.AWS_PROFILE)
            session.client('bedrock-runtime', region_name=config.AWS_REGION)
        except Exception as e:
            print(f"❌ Error: Cannot access AWS Bedrock with profile '{config.AWS_PROFILE}'")
            print(f"   Error: {str(e)}")
            print(f"   Please ensure AWS CLI is configured with the '{config.AWS_PROFILE}' profile")
            sys.exit(1)
    elif not config.ANTHROPIC_API_KEY and not config.OPENAI_API_KEY:
        print("❌ Error: No API access configured!")
        print("   Option 1: Use AWS Bedrock (default)")
        print("     - Set USE_AWS_BEDROCK=true in .env")
        print("     - Configure AWS CLI with 'diligent' profile")
        print("   Option 2: Use Anthropic API directly")
        print("     - Set USE_AWS_BEDROCK=false in .env")
        print("     - Set ANTHROPIC_API_KEY in .env")
        sys.exit(1)
    
    # Initialize orchestrator
    orchestrator = CreativityOrchestrator()
    
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
            
            for i, result in enumerate(results[:5], 1):
                idea = result['idea']
                eval = result['evaluation']
                
                print(f"\n{i}. {idea['idea_name']}")
                print(f"   Score: {eval['composite_score']:.3f} "
                      f"(N:{eval['novelty']:.2f} F:{eval['feasibility']:.2f} "
                      f"M:{eval['market_fit']:.2f} V:{eval['viability']:.2f})")
                print(f"   Problem: {idea['problem_statement'][:100]}...")
                print(f"   Target: {idea['target_user']}")
                print(f"   Differentiator: {idea['differentiator'][:80]}...")
            
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
            print(f"💾 Database: {report['database_path']}")
            
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
        
        elif args.command == 'export':
            # Export top ideas
            output_path = args.output or config.REPORTS_DIR / "exported_ideas.json"
            orchestrator.db.export_top_ideas_to_json(output_path, k=20)
            print(f"✅ Exported top 20 ideas to: {output_path}")
    
    finally:
        orchestrator.close()


if __name__ == "__main__":
    main()

