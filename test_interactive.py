#!/usr/bin/env python3
"""
Test script to demonstrate the interactive deployment analysis features
"""

import os
from dotenv import load_dotenv
from agent.react_agent import GitHubRepoReActAgent


def test_deployment_analysis():
    """Test the deployment feasibility analysis."""
    
    # Load environment variables
    load_dotenv()
    
    # Check if API key exists
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ Error: OPENROUTER_API_KEY not found in environment variables.")
        return
    
    print("🧪 Testing Interactive Deployment Analysis...")
    print("="*60)
    
    try:
        # Initialize the ReAct agent
        agent = GitHubRepoReActAgent(api_key)
        print("✅ Agent initialized successfully!")
        
        # Test with a simple repository that likely has deployment issues
        test_repo = "https://github.com/octocat/Hello-World"
        print(f"\n🔍 Testing deployment analysis for: {test_repo}")
        
        # Test deployment feasibility analysis
        analysis_prompt = f"""
        Analyze {test_repo} for deployment feasibility.
        
        Check for:
        1. Hardcoded localhost or development configurations
        2. Missing environment variables or configuration files
        3. Deployment blockers that would prevent production deployment
        4. Missing infrastructure requirements
        
        Provide a summary of deployment readiness and any issues found.
        Clone the repository, examine files, and clean up after analysis.
        """
        
        result = agent.ask_question(analysis_prompt)
        
        if result.get("success"):
            print("\n📊 DEPLOYMENT FEASIBILITY TEST RESULTS:")
            print("-" * 60)
            print(result['answer'])
            print("\n✅ Interactive deployment analysis test completed!")
        else:
            print(f"❌ Test failed: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ Test error: {str(e)}")


def demo_interactive_features():
    """Demonstrate the key interactive features."""
    print("\n🎯 INTERACTIVE DEPLOYMENT ANALYZER FEATURES:")
    print("="*60)
    
    features = [
        "🔍 Deployment Feasibility Analysis - Checks if code can be deployed",
        "⚠️ Deployment Blocker Detection - Finds hardcoded localhost, missing configs",
        "💬 Interactive Chat - Agent asks questions about missing information",
        "📊 Deployment Readiness Score - Rates deployment readiness 1-10",
        "🤖 Smart Consultation - Guides through deployment requirements",
        "✅ Customized Deployment Plan - Based on your specific responses"
    ]
    
    for feature in features:
        print(f"  {feature}")
    
    print("\n💡 Usage:")
    print("  python analyze_repo.py https://github.com/user/repo")
    print("\n🔄 Interactive Flow:")
    print("  1. Agent analyzes repository for deployment issues")
    print("  2. Agent asks you questions about missing configuration")
    print("  3. You provide environment variables, database details, etc.")
    print("  4. Agent provides customized deployment plan")
    print("  5. Get deployment readiness score and next steps")


if __name__ == "__main__":
    demo_interactive_features()
    test_deployment_analysis() 