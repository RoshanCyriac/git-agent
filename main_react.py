"""
Main application for GitHub Repository Analyzer using ReAct Agent
"""

import os
from dotenv import load_dotenv
from agent.react_agent import GitHubRepoReActAgent


def print_separator(title=""):
    """Print a formatted separator."""
    if title:
        print(f"\n{'='*80}")
        print(f"{title.center(80)}")
        print(f"{'='*80}")
    else:
        print("-" * 80)


def display_analysis_results(result):
    """Display analysis results in a formatted way."""
    if result.get("success"):
        print_separator("🤖 REACT AGENT ANALYSIS RESULTS")
        print(f"📁 Repository: {result['repository_url']}")
        print(f"🧠 Model Used: {result['model_used']}")
        print(f"🧹 Cleanup Performed: {'Yes' if result.get('cleanup_performed') else 'No'}")
        
        print("\n🔍 AI Analysis:")
        print_separator()
        print(result['analysis'])
    else:
        print(f"❌ Error: {result.get('error', 'Unknown error')}")


def display_comparison_results(result):
    """Display repository comparison results."""
    if result.get("success"):
        print_separator("🔄 REPOSITORY COMPARISON RESULTS")
        print("📁 Repositories Compared:")
        for i, repo in enumerate(result['repositories'], 1):
            print(f"  {i}. {repo}")
        print(f"\n🧠 Model Used: {result['model_used']}")
        
        print("\n🔍 Comparison Analysis:")
        print_separator()
        print(result['comparison'])
    else:
        print(f"❌ Error: {result.get('error', 'Unknown error')}")


def display_deployment_guide(result):
    """Display deployment guide results."""
    if result.get("success"):
        print_separator("🚀 DEPLOYMENT GUIDE")
        print(f"📁 Repository: {result['repository_url']}")
        print(f"🧠 Model Used: {result['model_used']}")
        
        print("\n📋 Deployment Instructions:")
        print_separator()
        print(result['deployment_guide'])
    else:
        print(f"❌ Error: {result.get('error', 'Unknown error')}")


def main():
    # Load environment variables
    load_dotenv()
    
    # Get API key from environment
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ Error: OPENROUTER_API_KEY not found in environment variables")
        return

    # Initialize the ReAct agent
    print("🚀 Initializing GitHub Repository ReAct Agent...")
    agent = GitHubRepoReActAgent(api_key)
    
    print("🤖 GitHub Repository Analyzer - ReAct Agent")
    print("This agent uses LangChain's ReAct framework with specialized repository tools!")
    print_separator()

    while True:
        print("\n🎯 ReAct Agent Options:")
        print("1. 📊 Analyze a repository (comprehensive analysis)")
        print("2. 🔄 Compare multiple repositories")
        print("3. 🚀 Get deployment guide for a repository")
        print("4. ❓ Ask a general question")
        print("5. 📋 List and manage cloned repositories")
        print("6. 🧹 Cleanup all repositories")
        print("7. 🚪 Exit")
        
        choice = input("\nEnter your choice (1-7): ").strip()
        
        if choice == "1":
            # Comprehensive repository analysis
            github_url = input("🔗 Enter GitHub repository URL: ").strip()
            cleanup = input("🧹 Clean up after analysis? (y/N): ").strip().lower() == 'y'
            
            print(f"\n🔄 ReAct Agent is analyzing: {github_url}")
            print("⏳ This may take several minutes as the agent explores the repository...")
            print("🧠 The agent will clone, explore, read files, and provide comprehensive insights.")
            
            result = agent.analyze_repository(github_url, cleanup_after=cleanup)
            display_analysis_results(result)
        
        elif choice == "2":
            # Compare repositories
            print("🔄 Repository Comparison")
            print("Enter repository URLs (press Enter on empty line to finish):")
            
            repo_urls = []
            while True:
                url = input(f"Repository {len(repo_urls) + 1} URL (or Enter to finish): ").strip()
                if not url:
                    break
                repo_urls.append(url)
            
            if len(repo_urls) < 2:
                print("❌ Need at least 2 repositories for comparison")
                continue
            
            print(f"\n🔄 ReAct Agent is comparing {len(repo_urls)} repositories...")
            print("⏳ This will take several minutes as each repository is analyzed...")
            
            result = agent.compare_repositories(repo_urls)
            display_comparison_results(result)
        
        elif choice == "3":
            # Get deployment guide
            github_url = input("🔗 Enter GitHub repository URL: ").strip()
            
            print(f"\n🚀 ReAct Agent is creating deployment guide for: {github_url}")
            print("⏳ Analyzing repository structure and configuration files...")
            
            result = agent.get_deployment_guide(github_url)
            display_deployment_guide(result)
        
        elif choice == "4":
            # Ask general question
            question = input("❓ Enter your question: ").strip()
            
            print(f"\n🧠 ReAct Agent is processing your question...")
            print("⏳ The agent will use available tools to answer...")
            
            result = agent.ask_question(question)
            
            if result.get("success"):
                print_separator("🤖 AGENT RESPONSE")
                print(f"❓ Question: {result['question']}")
                print(f"🧠 Model Used: {result['model_used']}")
                print("\n💬 Answer:")
                print_separator()
                print(result['answer'])
            else:
                print(f"❌ Error: {result.get('error', 'Unknown error')}")
        
        elif choice == "5":
            # List and manage repositories
            print("📋 Repository Management")
            print("⏳ Checking currently cloned repositories...")
            
            result = agent.ask_question("Please list all currently cloned repositories with their details.")
            
            if result.get("success"):
                print_separator("📋 CLONED REPOSITORIES")
                print(result['answer'])
                
                action = input("\n🔧 What would you like to do? (cleanup specific/all/nothing): ").strip().lower()
                if action in ['cleanup specific', 'specific']:
                    repo_name = input("Enter repository name to cleanup (owner/repo format): ").strip()
                    cleanup_result = agent.ask_question(f"Please cleanup the repository: {repo_name}")
                    if cleanup_result.get("success"):
                        print("✅ Cleanup result:")
                        print(cleanup_result['answer'])
                elif action in ['cleanup all', 'all']:
                    cleanup_result = agent.cleanup_all_repositories()
                    if cleanup_result.get("success"):
                        print("✅ Cleanup result:")
                        print(cleanup_result['cleanup_result'])
            else:
                print(f"❌ Error: {result.get('error', 'Unknown error')}")
        
        elif choice == "6":
            # Cleanup all repositories
            print("🧹 Cleaning up all repositories...")
            result = agent.cleanup_all_repositories()
            
            if result.get("success"):
                print("✅ Cleanup completed:")
                print(result['cleanup_result'])
            else:
                print(f"❌ Error: {result.get('error', 'Unknown error')}")
        
        elif choice == "7":
            # Exit
            print("🧹 Cleaning up before exit...")
            agent.cleanup_all_repositories()
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice. Please enter 1-7.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🧹 Cleaning up...")
        print("👋 Goodbye!") 