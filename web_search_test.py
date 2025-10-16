"""
Test script for web search integration
"""
import argparse
from core.web_search import get_search_engine
from config import config


def test_basic_search():
    """Test basic search functionality"""
    print("\n" + "="*70)
    print("🔍 TEST 1: Basic Web Search")
    print("="*70)
    
    if not config.SERPER_API_KEY:
        print("❌ SERPER_API_KEY not found in .env file")
        print("   Please add SERPER_API_KEY=your_key_here to your .env file")
        return False
    
    try:
        search_engine = get_search_engine()
        
        query = "GRC SaaS products 2024"
        print(f"\nQuery: \"{query}\"")
        print("-"*70)
        
        results = search_engine.search(query, num_results=3)
        
        if results:
            print(f"\n✅ Found {len(results)} results:\n")
            for i, result in enumerate(results, 1):
                print(f"{i}. {result.title}")
                print(f"   {result.snippet[:100]}...")
                print(f"   {result.link}\n")
            return True
        else:
            print("⚠️  No results found")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def test_competitor_search():
    """Test competitor search"""
    print("\n" + "="*70)
    print("🔍 TEST 2: Competitor Search")
    print("="*70)
    
    try:
        search_engine = get_search_engine()
        
        domain = "GRC"
        product_type = "CRM"
        print(f"\nSearching for: {product_type} competitors in {domain}")
        print("-"*70)
        
        results = search_engine.search_competitors(domain, product_type, num_results=3)
        
        if results:
            print(f"\n✅ Found {len(results)} competitor results:\n")
            for i, result in enumerate(results, 1):
                print(f"{i}. {result.title}")
                print(f"   {result.snippet[:100]}...")
                print()
            return True
        else:
            print("⚠️  No results found")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def test_market_trends():
    """Test market trends search"""
    print("\n" + "="*70)
    print("🔍 TEST 3: Market Trends Search")
    print("="*70)
    
    try:
        search_engine = get_search_engine()
        
        domain = "Healthcare"
        topic = "AI compliance automation"
        print(f"\nSearching for: {topic} trends in {domain}")
        print("-"*70)
        
        results = search_engine.search_market_trends(domain, topic, num_results=3)
        
        if results:
            print(f"\n✅ Found {len(results)} market trend results:\n")
            for i, result in enumerate(results, 1):
                print(f"{i}. {result.title}")
                print(f"   {result.snippet[:100]}...")
                print()
            return True
        else:
            print("⚠️  No results found")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def test_pricing_search():
    """Test pricing search"""
    print("\n" + "="*70)
    print("🔍 TEST 4: Pricing Search")
    print("="*70)
    
    try:
        search_engine = get_search_engine()
        
        product = "ServiceNow"
        domain = "ITSM"
        print(f"\nSearching for: {product} {domain} pricing")
        print("-"*70)
        
        results = search_engine.search_pricing(product, domain, num_results=3)
        
        if results:
            print(f"\n✅ Found {len(results)} pricing results:\n")
            for i, result in enumerate(results, 1):
                print(f"{i}. {result.title}")
                print(f"   {result.snippet[:100]}...")
                print()
            return True
        else:
            print("⚠️  No results found")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def test_format_for_prompt():
    """Test formatting results for LLM prompt"""
    print("\n" + "="*70)
    print("🔍 TEST 5: Format Results for Prompt")
    print("="*70)
    
    try:
        search_engine = get_search_engine()
        
        results = search_engine.search("CRM for GRC market", num_results=3)
        
        if results:
            formatted = search_engine.format_results_for_prompt(results, max_length=500)
            print("\n✅ Formatted output:\n")
            print(formatted)
            print(f"\nLength: {len(formatted)} characters")
            return True
        else:
            print("⚠️  No results found")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Test web search integration")
    parser.add_argument(
        "--test",
        choices=["basic", "competitors", "trends", "pricing", "format", "all"],
        default="all",
        help="Which test to run"
    )
    
    args = parser.parse_args()
    
    print("\n╔═══════════════════════════════════════════════════════════════════╗")
    print("║                                                                   ║")
    print("║          WEB SEARCH INTEGRATION TEST                              ║")
    print("║                                                                   ║")
    print("╚═══════════════════════════════════════════════════════════════════╝")
    
    results = {}
    
    if args.test in ["basic", "all"]:
        results["basic"] = test_basic_search()
    
    if args.test in ["competitors", "all"]:
        results["competitors"] = test_competitor_search()
    
    if args.test in ["trends", "all"]:
        results["trends"] = test_market_trends()
    
    if args.test in ["pricing", "all"]:
        results["pricing"] = test_pricing_search()
    
    if args.test in ["format", "all"]:
        results["format"] = test_format_for_prompt()
    
    # Summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name.capitalize()}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Web search is ready to use.")
    elif passed > 0:
        print("\n⚠️  Some tests passed. Check your SERPER_API_KEY and internet connection.")
    else:
        print("\n❌ All tests failed. Please check:")
        print("   1. SERPER_API_KEY is set in .env file")
        print("   2. API key is valid")
        print("   3. Internet connection is working")
    
    print()


if __name__ == "__main__":
    main()

