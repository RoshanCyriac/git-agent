#!/usr/bin/env python3
"""
Simple test script to verify the GitHub Repository ReAct Agent works.
"""

import os
from dotenv import load_dotenv

def test_agent():
    """Test that the ReAct agent can be imported and initialized."""
    
    # Load environment variables
    load_dotenv()
    
    # Get API key
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ Error: OPENROUTER_API_KEY not found in environment variables.")
        print("Please add your API key to the .env file.")
        return False
    
    try:
        # Test import
        from agent.react_agent import GitHubRepoReActAgent
        print("✅ Successfully imported GitHubRepoReActAgent")
        
        # Test initialization
        agent = GitHubRepoReActAgent(api_key)
        print("✅ Successfully initialized ReAct agent")
        
        print("🎉 All tests passed! The agent is ready to use.")
        print("Run 'python main_react.py' to start the interactive application.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_agent() 