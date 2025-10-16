"""
Test and demonstration of error recovery capabilities
"""
import argparse
import json
from pathlib import Path
from datetime import datetime
from core.error_recovery import get_error_recovery_engine
from agents import GeneratorAgent, CriticAgent


def test_error_recovery_with_generation():
    """Test error recovery with actual idea generation"""
    print("\n" + "=" * 70)
    print("🔧 ERROR RECOVERY TEST: Idea Generation")
    print("=" * 70)
    
    # Create generator agent with error recovery enabled
    generator = GeneratorAgent()
    
    print("\n✅ Generator Agent initialized with error recovery enabled")
    print(f"   Model: {generator.model}")
    print(f"   Max Retries: {generator.error_recovery_engine.max_retries}")
    
    # Test 1: Normal generation (should work)
    print("\n📝 Test 1: Normal Idea Generation")
    print("-" * 70)
    try:
        ideas = generator.execute(domain="Healthcare", num_ideas=2)
        print(f"✅ Generated {len(ideas)} ideas successfully")
        for i, idea in enumerate(ideas, 1):
            print(f"   {i}. {idea.idea_name}")
    except Exception as e:
        print(f"❌ Generation failed: {str(e)}")
    
    # Get error statistics
    stats = generator.get_error_statistics()
    if stats:
        print("\n📊 Error Recovery Statistics After Test:")
        print(f"   Total Unique Errors: {stats['total_unique_errors']}")
        print(f"   Recovery Attempts: {stats['total_recovery_attempts']}")
        print(f"   Successful Recoveries: {stats['successful_recoveries']}")
        print(f"   Failed Recoveries: {stats['failed_recoveries']}")
        if stats['total_recovery_attempts'] > 0:
            print(f"   Success Rate: {stats['recovery_success_rate']*100:.1f}%")


def test_error_recovery_with_critic():
    """Test error recovery with critic evaluation"""
    print("\n" + "=" * 70)
    print("🔧 ERROR RECOVERY TEST: Critic Evaluation")
    print("=" * 70)
    
    # Create critic agent
    critic = CriticAgent()
    
    print("\n✅ Critic Agent initialized with error recovery enabled")
    
    # Create a simple test idea
    from core.models import SaaSIdea
    test_idea = SaaSIdea(
        idea_id="test-001",
        idea_name="AI-Powered Testing Tool",
        problem_statement="Manual testing is slow and error-prone",
        solution_overview="Automated testing with AI insights",
        target_market="Software development teams",
        key_features=["Automated test generation", "Smart bug detection"],
        business_model="Subscription-based SaaS",
        competitive_advantage="AI-powered insights",
        implementation_complexity="Medium",
        estimated_timeline="6 months"
    )
    
    print("\n📝 Test: Evaluate Single Idea")
    print("-" * 70)
    try:
        evaluations = critic.execute([test_idea])
        print(f"✅ Evaluated idea successfully")
        eval = evaluations[0]
        print(f"   Novelty: {eval.novelty:.2f}")
        print(f"   Feasibility: {eval.feasibility:.2f}")
        print(f"   Market Fit: {eval.market_fit:.2f}")
        print(f"   Composite Score: {eval.composite_score:.2f}")
    except Exception as e:
        print(f"❌ Evaluation failed: {str(e)}")
    
    # Get statistics
    stats = critic.get_error_statistics()
    if stats:
        print("\n📊 Error Recovery Statistics:")
        print(f"   Total Unique Errors: {stats['total_unique_errors']}")
        print(f"   Recovery Attempts: {stats['total_recovery_attempts']}")
        if stats['total_recovery_attempts'] > 0:
            print(f"   Success Rate: {stats['recovery_success_rate']*100:.1f}%")


def view_global_error_statistics():
    """View global error recovery statistics"""
    print("\n" + "=" * 70)
    print("📊 GLOBAL ERROR RECOVERY STATISTICS")
    print("=" * 70)
    
    engine = get_error_recovery_engine()
    stats = engine.get_error_statistics()
    
    print(f"\n📈 Overall Statistics:")
    print(f"   Total Unique Errors: {stats['total_unique_errors']}")
    print(f"   Total Recovery Attempts: {stats['total_recovery_attempts']}")
    print(f"   Successful Recoveries: {stats['successful_recoveries']}")
    print(f"   Failed Recoveries: {stats['failed_recoveries']}")
    
    if stats['total_recovery_attempts'] > 0:
        success_rate = stats['recovery_success_rate'] * 100
        print(f"   Overall Success Rate: {success_rate:.1f}%")
        
        # Color-coded grade
        if success_rate >= 90:
            grade = "🟢 Excellent"
        elif success_rate >= 75:
            grade = "🟡 Good"
        elif success_rate >= 50:
            grade = "🟠 Fair"
        else:
            grade = "🔴 Needs Improvement"
        print(f"   Grade: {grade}")
    
    if stats['error_type_distribution']:
        print(f"\n📋 Error Type Distribution:")
        for error_type, count in stats['error_type_distribution'].items():
            print(f"   {error_type}: {count} occurrences")
    
    if stats['most_common_errors']:
        print(f"\n⚠️  Most Common Errors:")
        for i, (error_key, count) in enumerate(stats['most_common_errors'][:5], 1):
            error_parts = error_key.split(':', 1)
            error_type = error_parts[0]
            error_msg = error_parts[1][:60] + "..." if len(error_parts) > 1 else ""
            print(f"   {i}. [{error_type}] {error_msg}")
            print(f"      Occurrences: {count}")


def save_error_report(output_path: str):
    """Save comprehensive error report"""
    engine = get_error_recovery_engine()
    
    # Create reports directory if it doesn't exist
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    
    # Generate timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save error patterns
    patterns_file = reports_dir / f"error_patterns_{timestamp}.json"
    engine.save_error_patterns(str(patterns_file))
    
    print(f"\n✅ Error report saved to: {patterns_file}")
    
    # Also save a markdown report
    stats = engine.get_error_statistics()
    md_file = reports_dir / f"error_report_{timestamp}.md"
    
    with open(md_file, 'w') as f:
        f.write(f"# Error Recovery Report\n\n")
        f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"## Summary\n\n")
        f.write(f"- **Total Unique Errors**: {stats['total_unique_errors']}\n")
        f.write(f"- **Total Recovery Attempts**: {stats['total_recovery_attempts']}\n")
        f.write(f"- **Successful Recoveries**: {stats['successful_recoveries']}\n")
        f.write(f"- **Failed Recoveries**: {stats['failed_recoveries']}\n")
        
        if stats['total_recovery_attempts'] > 0:
            success_rate = stats['recovery_success_rate'] * 100
            f.write(f"- **Success Rate**: {success_rate:.1f}%\n")
        
        if stats['error_type_distribution']:
            f.write(f"\n## Error Type Distribution\n\n")
            for error_type, count in sorted(stats['error_type_distribution'].items(), 
                                          key=lambda x: x[1], reverse=True):
                f.write(f"- **{error_type}**: {count} occurrences\n")
        
        if stats['most_common_errors']:
            f.write(f"\n## Most Common Errors\n\n")
            for i, (error_key, count) in enumerate(stats['most_common_errors'][:10], 1):
                error_parts = error_key.split(':', 1)
                error_type = error_parts[0]
                error_msg = error_parts[1] if len(error_parts) > 1 else ""
                f.write(f"\n### {i}. {error_type}\n\n")
                f.write(f"**Occurrences**: {count}\n\n")
                f.write(f"**Message**: {error_msg}\n\n")
    
    print(f"✅ Markdown report saved to: {md_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Test and demonstrate error recovery capabilities"
    )
    parser.add_argument(
        "--test",
        choices=["generator", "critic", "all"],
        default="all",
        help="Which component to test"
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="View global error statistics"
    )
    parser.add_argument(
        "--save-report",
        action="store_true",
        help="Save error recovery report"
    )
    
    args = parser.parse_args()
    
    print("\n" + "=" * 70)
    print("🔧 ERROR RECOVERY SYSTEM TEST")
    print("=" * 70)
    print("\nThis script tests the self-debugging and error recovery capabilities")
    print("of the multi-agent system. The system will automatically:")
    print("  • Detect errors in LLM responses")
    print("  • Analyze error patterns")
    print("  • Retry with improved prompts")
    print("  • Learn from successes and failures")
    
    if args.stats:
        view_global_error_statistics()
    elif args.save_report:
        save_error_report("reports/error_recovery_report.json")
    else:
        if args.test in ["generator", "all"]:
            test_error_recovery_with_generation()
        
        if args.test in ["critic", "all"]:
            test_error_recovery_with_critic()
        
        # Show global statistics at the end
        view_global_error_statistics()
    
    print("\n" + "=" * 70)
    print("✅ ERROR RECOVERY TEST COMPLETE")
    print("=" * 70)
    print("\nTip: Run with --save-report to save detailed error analysis")
    print()


if __name__ == "__main__":
    main()

