"""
Quick demo of the automated quality metrics system
"""
from core.models import SaaSIdea, Domain
from core.validation_metrics import IdeaQualityMetrics


def demo_metrics():
    """Demonstrate the metrics system with two example ideas"""
    
    print("\n" + "=" * 80)
    print("🎯 AUTOMATED QUALITY METRICS DEMO")
    print("=" * 80)
    
    metrics = IdeaQualityMetrics()
    
    # Example 1: Poor quality idea (vague, no numbers, generic)
    poor_idea = SaaSIdea(
        idea_name="CloudAnalytics",
        problem_statement="Companies need better analytics",
        target_user="Business users",
        core_features=[
            "Dashboard",
            "Reports",
            "AI insights"
        ],
        differentiator="Easy to use and AI-powered",
        tech_stack=["Python", "React"],
        revenue_model="Subscription",
        domain=Domain.CLOUD
    )
    
    # Example 2: High quality idea (specific, quantified, differentiated)
    good_idea = SaaSIdea(
        idea_name="ContractIQ",
        problem_statement=(
            "Mid-market companies waste 40+ hours/month manually tracking contract "
            "renewals, leading to $50K+ in missed savings opportunities and compliance "
            "risks from expired vendor agreements"
        ),
        target_user=(
            "VP of Procurement and Legal Operations Managers at mid-market companies "
            "(500-5000 employees) managing 50-500 vendor contracts annually"
        ),
        core_features=[
            "AI-powered contract ingestion that auto-extracts key dates, obligations, and spend data",
            "Proactive renewal alerts with cost optimization recommendations reducing review time by 85%",
            "Compliance risk dashboard with auto-flagging of regulatory violations",
            "Vendor benchmarking and spend analytics identifying $20K+ annual savings"
        ],
        differentiator=(
            "Unlike generic CLM tools like Salesforce, ContractIQ is purpose-built for "
            "mid-market teams with AI that learns company-specific contract patterns and "
            "provides actionable cost-saving recommendations, not just storage"
        ),
        tech_stack=["Python/FastAPI", "PostgreSQL", "OpenAI GPT-4", "React", "AWS"],
        revenue_model="Subscription",
        domain=Domain.CLOUD
    )
    
    # Compute metrics for both
    print("\n" + "-" * 80)
    print("📝 EXAMPLE 1: Poor Quality Idea (Baseline)")
    print("-" * 80)
    print(f"Idea Name: {poor_idea.idea_name}")
    print(f"Problem: {poor_idea.problem_statement}")
    print(f"Target: {poor_idea.target_user}")
    print(f"Differentiator: {poor_idea.differentiator}")
    
    poor_metrics = metrics.compute_all_metrics(poor_idea)
    
    print(f"\n📊 Automated Quality Scores:")
    print(f"  • Specificity:      {poor_metrics['specificity_score']:.3f}")
    print(f"  • Quantification:   {poor_metrics['quantification_score']:.3f}")
    print(f"  • Differentiation:  {poor_metrics['differentiation_score']:.3f}")
    print(f"  • Feasibility:      {poor_metrics['feasibility_score']:.3f}")
    print(f"  • Completeness:     {poor_metrics['completeness_score']:.3f}")
    print(f"  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"  • COMPOSITE SCORE:  {poor_metrics['composite_score']:.3f} "
          f"({metrics.get_score_interpretation(poor_metrics['composite_score'])})")
    
    # Explain what's wrong
    print(f"\n❌ Issues Identified:")
    if poor_metrics['specificity_score'] < 0.6:
        print(f"  • Specificity too low: Target user is vague ('business users'), "
              f"no company size, no volume/scale")
    if poor_metrics['quantification_score'] < 0.5:
        print(f"  • No quantification: Problem statement has no numbers (hours, dollars, risks)")
    if poor_metrics['differentiation_score'] < 0.6:
        print(f"  • Poor differentiation: Generic claims ('AI-powered', 'easy to use'), "
              f"no comparison to competitors")
    
    # Good idea
    print("\n" + "-" * 80)
    print("📝 EXAMPLE 2: High Quality Idea (After Improvements)")
    print("-" * 80)
    print(f"Idea Name: {good_idea.idea_name}")
    print(f"Problem: {good_idea.problem_statement[:100]}...")
    print(f"Target: {good_idea.target_user[:80]}...")
    print(f"Differentiator: {good_idea.differentiator[:80]}...")
    
    good_metrics = metrics.compute_all_metrics(good_idea)
    
    print(f"\n📊 Automated Quality Scores:")
    print(f"  • Specificity:      {good_metrics['specificity_score']:.3f} ✅")
    print(f"  • Quantification:   {good_metrics['quantification_score']:.3f} ✅")
    print(f"  • Differentiation:  {good_metrics['differentiation_score']:.3f} ✅")
    print(f"  • Feasibility:      {good_metrics['feasibility_score']:.3f} ✅")
    print(f"  • Completeness:     {good_metrics['completeness_score']:.3f} ✅")
    print(f"  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"  • COMPOSITE SCORE:  {good_metrics['composite_score']:.3f} "
          f"({metrics.get_score_interpretation(good_metrics['composite_score'])})")
    
    print(f"\n✅ Strengths Identified:")
    if good_metrics['specificity_score'] >= 0.8:
        print(f"  • High specificity: Target includes role, company size (500-5000), "
              f"and volume (50-500 contracts)")
    if good_metrics['quantification_score'] >= 0.7:
        print(f"  • Well quantified: Multiple numbers ($50K, 40 hours/month, 85% reduction)")
    if good_metrics['differentiation_score'] >= 0.7:
        print(f"  • Clear differentiation: Compares to Salesforce, explains 'why us' "
              f"(learns patterns, provides recommendations)")
    
    # Show improvement
    improvement = ((good_metrics['composite_score'] - poor_metrics['composite_score']) 
                   / poor_metrics['composite_score'] * 100)
    
    print(f"\n" + "=" * 80)
    print(f"📈 IMPROVEMENT COMPARISON")
    print(f"=" * 80)
    print(f"Poor Idea Score:  {poor_metrics['composite_score']:.3f} "
          f"({metrics.get_score_interpretation(poor_metrics['composite_score'])})")
    print(f"Good Idea Score:  {good_metrics['composite_score']:.3f} "
          f"({metrics.get_score_interpretation(good_metrics['composite_score'])})")
    print(f"Improvement:      +{improvement:.1f}% 🚀")
    
    print(f"\n💡 Key Takeaways:")
    print(f"  1. Specificity matters: Include role + company size + volume/scale")
    print(f"  2. Quantify everything: Add hours, dollars, percentages")
    print(f"  3. Differentiate clearly: Compare to alternatives, explain 'why us'")
    print(f"  4. Target 0.7+ for production-ready ideas")
    print(f"\n" + "=" * 80 + "\n")


if __name__ == '__main__':
    demo_metrics()

