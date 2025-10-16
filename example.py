"""
Example script demonstrating how to use the Multi-Agent Creativity System programmatically
"""
from config import config
from core.orchestrator import CreativityOrchestrator
from core.models import Domain


def example_single_batch():
    """Example: Generate a single batch of ideas"""
    print("=" * 80)
    print("EXAMPLE 1: Single Batch Generation")
    print("=" * 80)
    
    orchestrator = CreativityOrchestrator()
    
    # Generate 5 ideas in the GRC domain
    results = orchestrator.generate_single_batch(
        domain="GRC",
        num_ideas=5
    )
    
    # Display results
    print("\n🎯 Top 3 Ideas:\n")
    for i, result in enumerate(results[:3], 1):
        idea = result['idea']
        eval = result['evaluation']
        
        print(f"{i}. {idea['idea_name']}")
        print(f"   Score: {eval['composite_score']:.3f}")
        print(f"   Problem: {idea['problem_statement'][:80]}...")
        print(f"   Target: {idea['target_user']}")
        print()
    
    orchestrator.close()


def example_creative_loop():
    """Example: Run the full creative loop"""
    print("=" * 80)
    print("EXAMPLE 2: Full Creative Loop")
    print("=" * 80)
    
    orchestrator = CreativityOrchestrator()
    
    # Run creative loop
    report = orchestrator.run_creative_loop(
        domain="DevOps",
        initial_ideas=3,  # Fewer ideas for faster demo
        max_iterations=3  # Just 3 iterations for demo
    )
    
    # Display summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total Iterations: {report['total_iterations']}")
    print(f"Total Ideas Generated: {report['total_ideas_generated']}")
    print(f"Best Score Achieved: {report['best_score']:.3f}")
    print(f"Average Score: {report['average_score']:.3f}")
    
    print("\n📈 Score Progression:")
    for i, score in enumerate(report['score_progression'], 1):
        bar = "█" * int(score * 40)
        print(f"  Iteration {i}: {bar} {score:.3f}")
    
    print(f"\n💾 Results saved to: {report['output_file']}")
    
    orchestrator.close()


def example_custom_domain():
    """Example: Generate ideas for multiple domains"""
    print("=" * 80)
    print("EXAMPLE 3: Multi-Domain Generation")
    print("=" * 80)
    
    orchestrator = CreativityOrchestrator()
    
    domains = ["DevOps", "GRC", "Cloud Infrastructure"]
    
    for domain in domains:
        print(f"\n🎯 Generating ideas for: {domain}")
        print("-" * 60)
        
        results = orchestrator.generate_single_batch(
            domain=domain,
            num_ideas=3
        )
        
        # Show top idea
        top = results[0]
        print(f"Top Idea: {top['idea']['idea_name']}")
        print(f"Score: {top['evaluation']['composite_score']:.3f}")
        print(f"Problem: {top['idea']['problem_statement'][:100]}...")
    
    orchestrator.close()


def example_access_database():
    """Example: Access stored ideas from database"""
    print("=" * 80)
    print("EXAMPLE 4: Accessing Stored Ideas")
    print("=" * 80)
    
    orchestrator = CreativityOrchestrator()
    
    # First, generate some ideas
    print("\n1. Generating ideas...")
    orchestrator.generate_single_batch(domain="AI/ML Operations", num_ideas=3)
    
    # Access top ideas from database
    print("\n2. Retrieving top ideas from database...")
    top_ideas = orchestrator.db.get_top_ideas(k=5)
    
    print(f"\n📋 Top {len(top_ideas)} Ideas in Database:\n")
    for i, idea_dict in enumerate(top_ideas, 1):
        print(f"{i}. {idea_dict['idea_name']}")
        print(f"   Domain: {idea_dict['domain']}")
        print(f"   Score: {idea_dict['composite_score']:.3f}")
        print()
    
    # Get all ideas count
    all_ideas = orchestrator.db.get_all_ideas()
    print(f"Total ideas in database: {len(all_ideas)}")
    
    # Export to JSON
    output_path = config.REPORTS_DIR / "example_export.json"
    orchestrator.db.export_top_ideas_to_json(output_path, k=10)
    print(f"\n💾 Exported top 10 ideas to: {output_path}")
    
    orchestrator.close()


def example_scoring_details():
    """Example: Understanding the scoring system"""
    print("=" * 80)
    print("EXAMPLE 5: Scoring System Details")
    print("=" * 80)
    
    orchestrator = CreativityOrchestrator()
    
    # Generate ideas
    print("\nGenerating ideas with detailed scoring...")
    results = orchestrator.generate_single_batch(domain="Cybersecurity", num_ideas=3)
    
    print("\n📊 Detailed Scoring Breakdown:\n")
    for i, result in enumerate(results, 1):
        idea = result['idea']
        eval = result['evaluation']
        
        print(f"{i}. {idea['idea_name']}")
        print(f"   " + "-" * 60)
        print(f"   Novelty:      {eval['novelty']:.3f} (weight: {config.NOVELTY_WEIGHT})")
        print(f"   Feasibility:  {eval['feasibility']:.3f} (weight: {config.FEASIBILITY_WEIGHT})")
        print(f"   Market Fit:   {eval['market_fit']:.3f} (weight: {config.MARKET_FIT_WEIGHT})")
        print(f"   Viability:    {eval['viability']:.3f} (weight: {config.VIABILITY_WEIGHT})")
        print(f"   " + "-" * 60)
        print(f"   COMPOSITE:    {eval['composite_score']:.3f}")
        print(f"\n   Calculation: {config.NOVELTY_WEIGHT}×{eval['novelty']:.3f} + "
              f"{config.FEASIBILITY_WEIGHT}×{eval['feasibility']:.3f} + "
              f"{config.MARKET_FIT_WEIGHT}×{eval['market_fit']:.3f} + "
              f"{config.VIABILITY_WEIGHT}×{eval['viability']:.3f}")
        print(f"                = {eval['composite_score']:.3f}")
        print()
    
    orchestrator.close()


if __name__ == "__main__":
    # Check if API keys are configured
    if not config.OPENAI_API_KEY and not config.ANTHROPIC_API_KEY:
        print("❌ ERROR: No API keys found!")
        print("   Please set OPENAI_API_KEY or ANTHROPIC_API_KEY in your .env file")
        exit(1)
    
    print("\n🚀 Multi-Agent Creativity System - Examples\n")
    
    # Run examples
    # Uncomment the examples you want to run:
    
    example_single_batch()
    # example_creative_loop()
    # example_custom_domain()
    # example_access_database()
    # example_scoring_details()
    
    print("\n✅ Examples complete!")
    print("\nTip: Edit example.py to run different examples or create your own!")

