#!/usr/bin/env python3
"""
Demo script for GitHub Repository Deployment Analyzer Web Interface
Shows how to start and use the beautiful web frontend
"""

import os
import sys
import time
import subprocess
import webbrowser
from dotenv import load_dotenv

def check_requirements():
    """Check if all requirements are installed."""
    try:
        import flask
        import flask_socketio
        from agent.react_agent import GitHubRepoReActAgent
        print("✅ All requirements are installed!")
        return True
    except ImportError as e:
        print(f"❌ Missing requirement: {e}")
        print("💡 Run: pip install -r requirements.txt")
        return False

def check_api_key():
    """Check if API key is configured."""
    load_dotenv()
    api_key = os.getenv("OPENROUTER_API_KEY")
    if api_key:
        print("✅ API key is configured!")
        return True
    else:
        print("❌ API key not found!")
        print("💡 Please add OPENROUTER_API_KEY to your .env file")
        return False

def start_web_interface():
    """Start the web interface."""
    print("\n🚀 Starting GitHub Repository Deployment Analyzer Web Interface...")
    print("="*80)
    
    # Check requirements
    if not check_requirements():
        return False
    
    # Check API key
    if not check_api_key():
        return False
    
    print("\n🌐 Web Interface Features:")
    print("  • 📊 Real-time analysis progress")
    print("  • 💬 Interactive chat with AI agent")
    print("  • 🎯 Beautiful, responsive design")
    print("  • ⚡ WebSocket communication")
    print("  • 📱 Works on desktop, tablet, and mobile")
    
    print("\n📋 How to Use:")
    print("  1. Enter a GitHub repository URL")
    print("  2. Click 'Analyze' to start")
    print("  3. Watch real-time progress updates")
    print("  4. Answer questions from the AI agent")
    print("  5. Get your deployment assessment")
    
    print("\n🎯 Example Repositories to Try:")
    print("  • https://github.com/tiangolo/fastapi")
    print("  • https://github.com/pallets/flask")
    print("  • https://github.com/django/django")
    print("  • https://github.com/octocat/Hello-World")
    
    print("\n⏳ Starting web server...")
    print("📱 The web interface will open in your browser automatically")
    print("🔗 Manual URL: http://localhost:5000")
    print("\n💡 Press Ctrl+C to stop the server")
    print("="*80)
    
    # Start the web server
    try:
        # Wait a moment then open browser
        def open_browser():
            time.sleep(2)
            webbrowser.open('http://localhost:5000')
        
        import threading
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        # Start Flask app
        from app import app, socketio
        socketio.run(app, debug=False, host='0.0.0.0', port=5000)
        
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down web server...")
        print("✅ Thanks for using GitHub Repository Deployment Analyzer!")
        return True
    except Exception as e:
        print(f"\n❌ Error starting web server: {e}")
        return False

def main():
    """Main function."""
    print("🚀 GitHub Repository Deployment Analyzer")
    print("🌐 Beautiful Web Interface Demo")
    print("="*50)
    
    if len(sys.argv) > 1 and sys.argv[1] == '--help':
        print("\nUsage:")
        print("  python demo_web.py           # Start web interface")
        print("  python demo_web.py --help    # Show this help")
        print("\nFeatures:")
        print("  • Real-time deployment analysis")
        print("  • Interactive AI consultation")
        print("  • Beautiful, responsive design")
        print("  • WebSocket communication")
        print("  • Deployment readiness scoring")
        return
    
    success = start_web_interface()
    
    if success:
        print("\n✅ Web interface demo completed successfully!")
    else:
        print("\n❌ Demo failed. Please check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 