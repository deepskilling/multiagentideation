"""
Deep Ideation Tool - Generate novel features using Pain Point Mining and Trend Analysis

This tool combines customer pain points with emerging trends to predict novel features
that don't exist yet but will be critical in the future.
"""
import argparse
import json
from pathlib import Path
from datetime import datetime
from config import config
from agents.pain_point_agent import PainPointAgent
from agents.trend_analysis_agent import TrendAnalysisAgent
from agents.generator_agent import GeneratorAgent
from agents.base_agent import BaseAgent
from core.web_search import get_search_engine


def deep_ideation(domain: str, num_ideas: int = 10, use_web_search: bool = True,
                 competitors: list = None, time_horizon: str = "2-3 years",
                 output_file: str = None):
    """
    Generate novel features using deep ideation
    
    Args:
        domain: Domain or product to ideate for
        num_ideas: Number of ideas to generate
        use_web_search: Whether to use web search
        competitors: List of competitor products to analyze
        time_horizon: How far ahead to predict
        output_file: Optional output file path
    """
    print("\n" + "="*80)
    print("🔮 DEEP IDEATION - Novel Feature Prediction")
    print("="*80)
    print(f"Domain: {domain}")
    print(f"Ideas to Generate: {num_ideas}")
    print(f"Time Horizon: {time_horizon}")
    print(f"Web Search: {'Enabled' if use_web_search else 'Disabled'}")
    if competitors:
        print(f"Analyzing Competitors: {', '.join(competitors)}")
    print()
    
    # Phase 1: Mine Customer Pain Points
    print("\n📋 PHASE 1: Mining Customer Pain Points")
    print("-" * 80)
    
    pain_point_agent = PainPointAgent(use_web_search=use_web_search)
    pain_points = pain_point_agent.execute(
        product_or_domain=domain,
        competitor_products=competitors
    )
    
    # Display pain point summary
    print("\n✅ Pain Point Analysis Complete:")
    print(f"   Total Pain Points Found: {pain_points['total_pain_points']}")
    print(f"   Clusters: {len(pain_points['clustered_pain_points'])}")
    
    if pain_points.get('top_pain_points'):
        print("\n   🔥 Top 3 Pain Points:")
        for pp in pain_points['top_pain_points'][:3]:
            print(f"   {pp.get('rank')}. {pp.get('problem', '')}")
    
    # Phase 2: Analyze Trends
    print("\n\n🔮 PHASE 2: Analyzing Emerging Trends")
    print("-" * 80)
    
    trend_agent = TrendAnalysisAgent(use_web_search=use_web_search)
    trends = trend_agent.execute(
        domain=domain,
        time_horizon=time_horizon
    )
    
    # Display trend summary
    print("\n✅ Trend Analysis Complete:")
    print(f"   Total Trends Found: {trends['total_trends']}")
    print(f"   Categories: {len(trends['trend_categories'])}")
    
    if trends.get('key_predictions'):
        print("\n   🚀 Top 3 Predictions:")
        for pred in trends['key_predictions'][:3]:
            print(f"   {pred.get('rank')}. {pred.get('prediction', '')} ({pred.get('timeline', '')})")
    
    # Phase 3: Generate Novel Features
    print("\n\n💡 PHASE 3: Generating Novel Features")
    print("-" * 80)
    
    # Build enhanced prompt
    pain_point_context = pain_point_agent.format_for_generation(pain_points)
    trend_context = trend_agent.format_for_generation(trends)
    
    enhanced_prompt = f"""Generate {num_ideas} novel features for {domain} that:

1. Solve real customer pain points (identified from customer feedback)
2. Leverage emerging trends (technology and market trends for {time_horizon})
3. Don't exist in current products (truly novel)
4. Would be critical/essential in {time_horizon}

{pain_point_context}

{trend_context}

**Requirements:**
- Each feature should address at least one pain point AND leverage at least one trend
- Think first principles: challenge assumptions about how things "must" be done
- Be specific and actionable (not vague concepts)
- Consider 10x improvement, not 10%
- Include features competitors haven't thought of

Generate ideas as JSON array:
[
  {{
    "feature_name": "Name of the feature",
    "problem_solved": "Which pain point(s) this addresses",
    "trend_leveraged": "Which trend(s) this uses",
    "description": "What the feature does and how",
    "novel_aspect": "Why this doesn't exist yet / Why it's novel",
    "competitive_advantage": "Why this would be differentiated",
    "timing": "When this should be built (based on trend maturity)",
    "impact_score": "1-10 score for potential impact"
  }}
]
"""
    
    generator = GeneratorAgent()
    
    print(f"   Generating {num_ideas} novel features...")
    print(f"   Using: Pain points + Trends + First principles")
    
    try:
        response = generator._call_llm(
            prompt=enhanced_prompt,
            temperature=0.8,  # Higher temperature for creativity
            max_tokens=6000
        )
        
        # Parse JSON response
        response = response.strip()
        if "```json" in response:
            response = response.split("```json")[1].split("```")[0].strip()
        elif "```" in response:
            response = response.split("```")[1].split("```")[0].strip()
        
        features = json.loads(response)
        
        # Display features
        print(f"\n✅ Generated {len(features)} Novel Features:\n")
        print("=" * 80)
        
        for i, feature in enumerate(features, 1):
            print(f"\n{i}. {feature.get('feature_name', 'Unnamed Feature')}")
            print(f"   Impact Score: {feature.get('impact_score', 'N/A')}/10")
            print(f"   Problem Solved: {feature.get('problem_solved', '')}")
            print(f"   Trend Leveraged: {feature.get('trend_leveraged', '')}")
            print(f"   Description: {feature.get('description', '')}")
            print(f"   Novel Aspect: {feature.get('novel_aspect', '')}")
            print(f"   Competitive Advantage: {feature.get('competitive_advantage', '')}")
            print(f"   Timing: {feature.get('timing', '')}")
        
        # Prepare output
        output = {
            'metadata': {
                'domain': domain,
                'num_ideas': num_ideas,
                'time_horizon': time_horizon,
                'competitors_analyzed': competitors or [],
                'generated_at': datetime.utcnow().isoformat(),
                'web_search_enabled': use_web_search
            },
            'pain_points': pain_points,
            'trends': trends,
            'features': features
        }
        
        # Save to file
        if output_file is None:
            safe_domain = "".join(c if c.isalnum() or c in (' ', '_') else '_' for c in domain)[:50]
            output_file = config.REPORTS_DIR / f"deep_ideation_{safe_domain.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        else:
            output_file = Path(output_file)
        
        with open(output_file, 'w') as f:
            json.dump(output, f, indent=2, default=str)
        
        print(f"\n\n💾 Full results saved to: {output_file}")
        
        # Show cost summary
        llm_cost = BaseAgent.get_cost_summary()
        if llm_cost['total_api_calls'] > 0:
            print(f"\n💰 LLM Cost: ${llm_cost['total_cost_usd']:.4f}")
            print(f"   API Calls: {llm_cost['total_api_calls']}")
            print(f"   Total Tokens: {llm_cost['total_tokens']:,}")
        
        if use_web_search and config.SERPER_API_KEY:
            search_engine = get_search_engine()
            cost_summary = search_engine.get_cost_summary(assume_free_tier=True)
            if cost_summary['total_searches'] > 0:
                print(f"\n🔍 Web Searches: {cost_summary['total_searches']}")
                print(f"   Cost: ${cost_summary['cost_usd']:.3f} (Free Tier)")
                print(f"   Remaining Free: {cost_summary['free_tier_limit'] - cost_summary['total_searches']}")
                
                total_cost = llm_cost['total_cost_usd'] + cost_summary['cost_usd']
                print(f"\n💵 Total Session Cost: ${total_cost:.4f}")
        
        print("\n" + "=" * 80)
        print("✅ Deep Ideation Complete!")
        print("=" * 80)
        
        return output
        
    except Exception as e:
        print(f"\n❌ Error generating features: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Deep Ideation - Generate novel features using pain points and trends"
    )
    
    parser.add_argument(
        'domain',
        type=str,
        help='Domain or product to ideate for (e.g., "GRC software", "Healthcare AI")'
    )
    
    parser.add_argument(
        '--num-ideas',
        type=int,
        default=10,
        help='Number of novel features to generate (default: 10)'
    )
    
    parser.add_argument(
        '--competitors',
        type=str,
        nargs='+',
        help='Competitor products to analyze (e.g., "ServiceNow" "LogicGate")'
    )
    
    parser.add_argument(
        '--time-horizon',
        type=str,
        default='2-3 years',
        choices=['2-3 years', '3-5 years', '5+ years'],
        help='How far ahead to predict (default: 2-3 years)'
    )
    
    parser.add_argument(
        '--no-search',
        action='store_true',
        help='Disable web search (faster but less grounded in reality)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        help='Output file path (default: auto-generated in reports/)'
    )
    
    args = parser.parse_args()
    
    # Check for web search requirements
    use_search = not args.no_search
    if use_search and not config.SERPER_API_KEY:
        print("⚠️  Warning: Web search requested but SERPER_API_KEY not found")
        print("   Continuing without web search (will use LLM knowledge only)")
        use_search = False
    
    # Run deep ideation
    result = deep_ideation(
        domain=args.domain,
        num_ideas=args.num_ideas,
        use_web_search=use_search,
        competitors=args.competitors,
        time_horizon=args.time_horizon,
        output_file=args.output
    )
    
    if result is None:
        exit(1)


if __name__ == "__main__":
    main()

