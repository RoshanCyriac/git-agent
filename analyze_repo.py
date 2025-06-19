#!/usr/bin/env python3
"""
Interactive GitHub Repository Deployment Analyzer
Usage: python analyze_repo.py <github_url>
"""

import sys
import os
from dotenv import load_dotenv
from agent.react_agent import GitHubRepoReActAgent


def get_user_input(question):
    """Get input from user with colored prompt."""
    print(f"\n🤖 Agent Question: {question}")
    response = input("👤 Your Answer: ").strip()
    return response


def analyze_repo_interactive(github_url: str):
    """
    Analyze a repository with interactive deployment feasibility check.
    
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
        print("⏳ Performing comprehensive deployment analysis...")
        
        # Phase 1: Initial Analysis
        initial_prompt = f"""
        Analyze the GitHub repository: {github_url} for deployment feasibility.
        
        Perform a comprehensive analysis focusing on:

        ## DEPLOYMENT FEASIBILITY ANALYSIS
        1. **Code Quality Check**:
           - Look for hardcoded localhost URLs, IP addresses, or ports
           - Check for hardcoded file paths or system-specific paths
           - Identify any development-only configurations
           - Check for missing production configurations

        2. **Configuration Analysis**:
           - Identify required environment variables
           - Check for .env.example or configuration templates
           - Look for database connection strings
           - Find API endpoints and external service dependencies

        3. **Dependency Assessment**:
           - Analyze package files for production readiness
           - Check for development vs production dependencies
           - Identify potential security vulnerabilities
           - Look for version conflicts or outdated packages

        4. **Infrastructure Requirements**:
           - Database requirements and setup
           - External services needed (Redis, message queues, etc.)
           - Port requirements and networking
           - File system requirements

        ## DEPLOYMENT BLOCKERS
        Specifically identify any issues that would prevent deployment:
        - Hardcoded localhost/127.0.0.1 references
        - Missing environment variable configurations
        - Incomplete database setup
        - Missing production configurations
        - Security issues (exposed secrets, etc.)
        - Dependency conflicts

        ## MISSING INFORMATION
        List any information that would be needed from the user to proceed with deployment.

        Clone the repository, examine all relevant files, and provide a detailed feasibility report.
        Clean up after analysis.
        """
        
        # Run initial analysis
        print("📊 Phase 1: Initial deployment feasibility analysis...")
        result = agent.ask_question(initial_prompt)
        
        if not result.get("success"):
            print(f"❌ Analysis failed: {result.get('error')}")
            return False
        
        analysis = result['answer']
        
        # Display initial results
        print("\n" + "="*80)
        print("📋 INITIAL DEPLOYMENT ANALYSIS")
        print("="*80)
        print(analysis)
        
        # Phase 2: Interactive Q&A for missing information
        print("\n" + "="*80)
        print("🤖 INTERACTIVE DEPLOYMENT CONSULTATION")
        print("="*80)
        
        # Ask agent to identify questions for the user
        questions_prompt = f"""
        Based on the previous analysis of {github_url}, identify specific questions that need to be asked to the user to complete the deployment assessment.
        
        Focus on:
        1. Missing environment variables and their values
        2. Database configuration details
        3. External service configurations
        4. Domain/hosting preferences
        5. Scaling requirements
        6. Security configurations
        
        Provide a numbered list of specific questions that would help complete the deployment plan.
        Keep questions concise and focused on deployment requirements.
        
        Previous analysis:
        {analysis}
        """
        
        questions_result = agent.ask_question(questions_prompt)
        
        if questions_result.get("success"):
            questions_text = questions_result['answer']
            print("🤖 The agent has identified some questions to complete the deployment analysis:")
            print("-" * 80)
            print(questions_text)
            
            # Interactive Q&A session
            print("\n💬 Let's gather the missing information:")
            user_responses = []
            
            # Simple interactive session
            while True:
                question = get_user_input("What information can you provide? (or type 'done' to finish)")
                if question.lower() in ['done', 'finish', 'complete', 'exit']:
                    break
                if question:
                    user_responses.append(question)
            
            # Phase 3: Final deployment assessment with user input
            if user_responses:
                print("\n📋 Processing your responses...")
                
                final_prompt = f"""
                Based on the repository analysis of {github_url} and the user's responses, provide a final deployment assessment.
                
                Original Analysis:
                {analysis}
                
                User Responses:
                {chr(10).join([f"- {resp}" for resp in user_responses])}
                
                Now provide:
                
                ## DEPLOYMENT FEASIBILITY SUMMARY
                - ✅ READY TO DEPLOY: List what's properly configured
                - ⚠️ NEEDS ATTENTION: Issues that need to be fixed
                - ❌ DEPLOYMENT BLOCKERS: Critical issues preventing deployment
                
                ## STEP-BY-STEP DEPLOYMENT PLAN
                Provide detailed steps considering the user's responses:
                1. Prerequisites and setup
                2. Environment configuration
                3. Database setup
                4. Application configuration
                5. Build and deployment process
                6. Testing and verification
                
                ## DEPLOYMENT READINESS SCORE
                Give a score from 1-10 and explain the reasoning.
                
                ## NEXT STEPS
                Specific actions the user needs to take to make this deployable.
                """
                
                final_result = agent.ask_question(final_prompt)
                
                if final_result.get("success"):
                    print("\n" + "="*80)
                    print("🚀 FINAL DEPLOYMENT ASSESSMENT")
                    print("="*80)
                    print(f"📁 Repository: {github_url}")
                    print(f"🧠 Model: {final_result['model_used']}")
                    print("\n📋 Complete Deployment Analysis:")
                    print("-" * 80)
                    print(final_result['answer'])
                    return True
        
        # Fallback if no interactive session
        print("\n" + "="*80)
        print("🚀 DEPLOYMENT ANALYSIS RESULTS")
        print("="*80)
        print(f"📁 Repository: {github_url}")
        print(f"🧠 Model: {result['model_used']}")
        print("\n📋 Deployment Feasibility Report:")
        print("-" * 80)
        print(analysis)
        return True
            
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
    
    print("🚀 GitHub Repository Deployment Analyzer")
    print("Interactive deployment feasibility analysis with chat support")
    print("="*80)
    
    # Analyze the repository
    success = analyze_repo_interactive(github_url)
    
    if success:
        print("\n✅ Analysis completed successfully!")
        print("💡 Use the deployment plan above to proceed with your deployment.")
    else:
        print("\n❌ Analysis failed!")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Analysis interrupted!")
        sys.exit(1) 