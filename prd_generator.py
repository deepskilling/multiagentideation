"""
PRD Generator - Command-line tool to expand ideas into Product Requirements Documents
"""
import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

from config import config
from core.database import IdeaDatabase
from agents.prd_generator_agent import PRDGeneratorAgent


def main():
    """Main function for PRD generation"""
    parser = argparse.ArgumentParser(
        description="Generate Product Requirements Document from a SaaS idea"
    )
    
    parser.add_argument(
        'idea_id',
        type=str,
        nargs='?',
        help='ID of the idea to expand (or use --top to get best idea)'
    )
    
    parser.add_argument(
        '--top',
        action='store_true',
        help='Use the top-scored idea from database'
    )
    
    parser.add_argument(
        '--list',
        action='store_true',
        help='List all available ideas'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        help='Output file path (default: reports/prd_<idea_name>.json)'
    )
    
    parser.add_argument(
        '--feature',
        type=str,
        help='Generate deep dive for a specific feature'
    )
    
    parser.add_argument(
        '--format',
        choices=['json', 'markdown'],
        default='json',
        help='Output format'
    )
    
    args = parser.parse_args()
    
    # Initialize database
    db = IdeaDatabase()
    
    # List ideas if requested
    if args.list:
        ideas = db.get_all_ideas(limit=20)
        if not ideas:
            print("No ideas found in database. Generate some first!")
            sys.exit(0)
        
        print("\n📋 Available Ideas:\n")
        print(f"{'ID':<40} {'Name':<30} {'Domain':<20}")
        print("-" * 90)
        for idea in ideas:
            print(f"{idea['idea_id']:<40} {idea['idea_name']:<30} {idea['domain']:<20}")
        
        sys.exit(0)
    
    # Get idea
    if args.top:
        print("🔍 Getting top-scored idea...")
        top_ideas = db.get_top_ideas(k=1)
        if not top_ideas:
            print("❌ No ideas found in database!")
            sys.exit(1)
        idea_data = top_ideas[0]
    elif args.idea_id:
        print(f"🔍 Loading idea: {args.idea_id}")
        idea_data = db.get_idea(args.idea_id)
        if not idea_data:
            print(f"❌ Idea not found: {args.idea_id}")
            sys.exit(1)
    else:
        print("❌ Please provide an idea ID or use --top flag")
        print("   Use --list to see available ideas")
        sys.exit(1)
    
    # Convert dict to SaaSIdea object
    from core.models import SaaSIdea, Domain, RevenueModel
    
    idea = SaaSIdea(
        idea_id=idea_data['idea_id'],
        idea_name=idea_data['idea_name'],
        problem_statement=idea_data['problem_statement'],
        target_user=idea_data['target_user'],
        core_features=json.loads(idea_data['core_features']),
        differentiator=idea_data['differentiator'],
        tech_stack=json.loads(idea_data['tech_stack']),
        revenue_model=RevenueModel(idea_data['revenue_model']),
        domain=Domain(idea_data['domain'])
    )
    
    print(f"\n🚀 Generating PRD for: {idea.idea_name}")
    print(f"   Domain: {idea.domain}")
    print(f"   Target: {idea.target_user}")
    print()
    
    # Initialize PRD generator
    prd_generator = PRDGeneratorAgent()
    
    # Generate PRD or feature deep dive
    if args.feature:
        print(f"📝 Generating feature deep dive: {args.feature}")
        result = prd_generator.generate_feature_deep_dive(idea, args.feature)
    else:
        print("📝 Generating comprehensive PRD...")
        print("   (This may take 30-60 seconds)")
        result = prd_generator.execute(idea)
    
    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        safe_name = idea.idea_name.replace(' ', '_').replace('/', '_')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        if args.format == 'markdown':
            output_path = config.REPORTS_DIR / f"prd_{safe_name}_{timestamp}.md"
        else:
            output_path = config.REPORTS_DIR / f"prd_{safe_name}_{timestamp}.json"
    
    # Save output
    config.ensure_directories()
    
    if args.format == 'markdown':
        # Convert to markdown
        md_content = generate_markdown_prd(result, idea)
        with open(output_path, 'w') as f:
            f.write(md_content)
    else:
        # Save as JSON
        with open(output_path, 'w') as f:
            json.dump(result, f, indent=2, default=str)
    
    print(f"\n✅ PRD generated successfully!")
    print(f"📄 Saved to: {output_path}")
    
    # Display summary
    if 'product_name' in result and 'executive_summary' in result:
        print(f"\n📊 PRD Summary:")
        print(f"   Product: {result['product_name']}")
        if 'tagline' in result:
            print(f"   Tagline: {result['tagline']}")
        if 'mvp_features' in result.get('features', {}):
            print(f"   MVP Features: {len(result['features']['mvp_features'])}")
        if 'roadmap' in result:
            print(f"   Phases: {len([k for k in result['roadmap'].keys() if k.startswith('phase')])}")
    
    db.close()


def generate_markdown_prd(prd: dict, idea) -> str:
    """Convert PRD JSON to Markdown format"""
    md = f"""# Product Requirements Document
# {prd.get('product_name', idea.idea_name)}

**{prd.get('tagline', '')}**

---

## Executive Summary

{prd.get('executive_summary', {}).get('overview', 'N/A')}

### Objectives
"""
    
    for obj in prd.get('executive_summary', {}).get('objectives', []):
        md += f"- {obj}\n"
    
    md += "\n### Success Metrics\n"
    for metric in prd.get('executive_summary', {}).get('success_metrics', []):
        md += f"- {metric}\n"
    
    md += f"""
---

## Problem Statement

### User Pain Points
"""
    
    for pain in prd.get('problem_statement', {}).get('user_pain_points', []):
        md += f"- {pain}\n"
    
    # Add more sections as needed
    md += "\n---\n\n*Generated by Multi-Agent Creativity System*\n"
    
    return md


if __name__ == "__main__":
    main()

