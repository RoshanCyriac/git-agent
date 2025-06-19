#!/usr/bin/env python3
"""
Simple command-line GitHub Repository Deployment Analyzer
Usage: python analyze_repo.py <github_url>
"""

import sys
import os
from dotenv import load_dotenv
from agent.react_agent import GitHubRepoReActAgent


def analyze_repo(github_url: str):
    """
    Analyze a repository and provide comprehensive deployment information.
    
    Args:
        github_url: GitHub repository URL to analyze
    """
    # Load environment variables
    load_dotenv()
    
    # Get API key
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ Error: OPENROUTER_API_KEY not found in environment variables.")
        print("Please add your API key to the .env file.")
        return False
    
    try:
        # Initialize the ReAct agent
        agent = GitHubRepoReActAgent(api_key)
        
        print(f"🔍 Analyzing repository: {github_url}")
        print("⏳ Analyzing deployment requirements...")
        
        # Create comprehensive deployment analysis prompt
        deployment_prompt = f"""
        Analyze the GitHub repository: {github_url}
        
        Provide a comprehensive deployment and setup guide covering:

        ## ESSENTIAL FILES & DOCUMENTATION
        - README.md analysis (project description, installation instructions, prerequisites)
        - Package/dependency files (package.json, requirements.txt, etc.)

        ## CONFIGURATION & ENVIRONMENT  
        - Environment configuration (.env.example, config files)
        - Database and external service requirements
        - Runtime requirements (language versions, system dependencies)

        ## DEPLOYMENT FILES
        - Containerization (Dockerfile, docker-compose.yml)
        - CI/CD workflows and deployment scripts
        - Server configuration files

        ## ARCHITECTURE & BUILD
        - Project structure and entry points
        - Build process and commands
        - Testing procedures

        Provide step-by-step instructions for:
        1. Prerequisites installation
        2. Environment setup  
        3. Configuration
        4. Build process
        5. Running locally
        6. Production deployment
        7. Troubleshooting

        Clone the repository, examine all relevant files, and provide complete deployment information.
        Clean up after analysis.
        """
        
        # Run the analysis
        result = agent.ask_question(deployment_prompt)
        
        if result.get("success"):
            print("\n" + "="*80)
            print("🚀 DEPLOYMENT ANALYSIS RESULTS")
            print("="*80)
            print(f"📁 Repository: {github_url}")
            print(f"🧠 Model: {result['model_used']}")
            print("\n📋 Comprehensive Deployment Guide:")
            print("-" * 80)
            print(result['answer'])
            return True
        else:
            print(f"❌ Analysis failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def main():
    """Main function."""
    if len(sys.argv) != 2:
        print("Usage: python analyze_repo.py <github_url>")
        print("Example: python analyze_repo.py https://github.com/user/repo")
        sys.exit(1)
    
    github_url = sys.argv[1].strip()
    
    # Validate URL
    if not github_url.startswith('https://github.com/'):
        print("❌ Please provide a valid GitHub URL (should start with https://github.com/)")
        sys.exit(1)
    
    # Analyze the repository
    success = analyze_repo(github_url)
    
    if success:
        print("\n✅ Analysis completed successfully!")
    else:
        print("\n❌ Analysis failed!")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Analysis interrupted!")
        sys.exit(1) 