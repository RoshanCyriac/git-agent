#!/usr/bin/env python3
"""
Web Frontend for GitHub Repository Deployment Analyzer
Simple deployability check with clear yes/no answers
"""

import os
import json
import asyncio
import threading
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from dotenv import load_dotenv
from agent.react_agent import GitHubRepoReActAgent
import random
import string
import subprocess
import tempfile
import shutil
import logging
from langchain_openai import ChatOpenAI
from langchain.agents import create_react_agent, AgentExecutor
from langchain.tools import Tool
from langchain_core.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
socketio = SocketIO(app, cors_allowed_origins="*")

# Global variables for analysis state
analysis_sessions = {}
agent_instance = None


def initialize_agent():
    """Initialize the ReAct agent."""
    global agent_instance
    api_key = os.getenv("OPENROUTER_API_KEY")
    if api_key:
        agent_instance = GitHubRepoReActAgent(api_key)
        return True
    return False


def clone_repository_with_auth(github_url, github_token=None):
    """Clone a GitHub repository with optional authentication."""
    try:
        # Generate a unique local path
        repo_name = github_url.split('/')[-1].replace('.git', '')
        random_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        local_path = os.path.join(tempfile.gettempdir(), f"{repo_name}_{random_id}")
        
        if github_token:
            # Convert GitHub URL to authenticated URL
            if github_url.startswith('https://github.com/'):
                auth_url = github_url.replace('https://github.com/', f'https://{github_token}@github.com/')
            else:
                auth_url = github_url
            
            # Clone with authentication
            result = subprocess.run(
                ['git', 'clone', auth_url, local_path],
                capture_output=True,
                text=True,
                timeout=60
            )
        else:
            # Clone public repository
            result = subprocess.run(
                ['git', 'clone', github_url, local_path],
                capture_output=True,
                text=True,
                timeout=60
            )
        
        if result.returncode == 0:
            logger.info(f"Successfully cloned repository to {local_path}")
            return local_path
        else:
            logger.error(f"Failed to clone repository: {result.stderr}")
            return None
            
    except subprocess.TimeoutExpired:
        logger.error("Repository cloning timed out")
        return None
    except Exception as e:
        logger.error(f"Error cloning repository: {str(e)}")
        return None


def get_repository_structure(local_path):
    """Get the structure of the repository."""
    try:
        structure = []
        for root, dirs, files in os.walk(local_path):
            # Skip .git directory
            if '.git' in dirs:
                dirs.remove('.git')
            
            level = root.replace(local_path, '').count(os.sep)
            indent = ' ' * 2 * level
            rel_path = os.path.relpath(root, local_path)
            if rel_path != '.':
                structure.append(f"{indent}{os.path.basename(root)}/")
            
            subindent = ' ' * 2 * (level + 1)
            for file in files[:10]:  # Limit files per directory
                structure.append(f"{subindent}{file}")
            
            if len(files) > 10:
                structure.append(f"{subindent}... and {len(files) - 10} more files")
        
        return '\n'.join(structure[:100])  # Limit total lines
    except Exception as e:
        logger.error(f"Error getting repository structure: {str(e)}")
        return "Error reading repository structure"


def get_repository_content(local_path):
    """Get key content from the repository."""
    try:
        content_summary = []
        
        # Key files to analyze
        key_files = [
            'package.json', 'requirements.txt', 'Dockerfile', 'docker-compose.yml',
            'app.py', 'main.py', 'index.js', 'server.js', 'app.js',
            'README.md', '.env.example', 'config.py', 'settings.py'
        ]
        
        for file_name in key_files:
            file_path = os.path.join(local_path, file_name)
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()[:2000]  # Limit content size
                        content_summary.append(f"\n--- {file_name} ---\n{content}")
                except Exception as e:
                    content_summary.append(f"\n--- {file_name} ---\nError reading file: {str(e)}")
        
        return '\n'.join(content_summary)
    except Exception as e:
        logger.error(f"Error getting repository content: {str(e)}")
        return "Error reading repository content"


def cleanup_repository(local_path):
    """Clean up the cloned repository."""
    try:
        if local_path and os.path.exists(local_path):
            shutil.rmtree(local_path)
            logger.info(f"Cleaned up repository at {local_path}")
    except Exception as e:
        logger.error(f"Error cleaning up repository: {str(e)}")


def should_ask_questions(analysis_result, user_env_vars):
    """Determine if we need to ask additional questions."""
    # Check if analysis indicates missing information
    missing_indicators = [
        'missing information',
        'need more details',
        'unclear',
        'cannot determine',
        'additional information needed'
    ]
    
    analysis_lower = analysis_result.lower()
    needs_questions = any(indicator in analysis_lower for indicator in missing_indicators)
    
    # If user provided comprehensive env vars, reduce need for questions
    if user_env_vars and len(user_env_vars) > 3:
        return False
    
    return needs_questions


def emit_status(session_id, status, message, data=None):
    """Emit status updates to the frontend."""
    socketio.emit('analysis_update', {
        'session_id': session_id,
        'status': status,
        'message': message,
        'data': data,
        'timestamp': datetime.now().isoformat()
    }, room=session_id)


def run_analysis_phase(session_id, github_url, phase, prompt, phase_name):
    """Run a single analysis phase and emit results."""
    try:
        emit_status(session_id, 'processing', f'🔄 {phase_name}...')
        
        result = agent_instance.ask_question(prompt)
        
        if result.get("success"):
            emit_status(session_id, 'phase_complete', f'✅ {phase_name} completed', {
                'phase': phase,
                'result': result['answer'],
                'model_used': result.get('model_used', 'Unknown')
            })
            return result
        else:
            emit_status(session_id, 'error', f'❌ {phase_name} failed: {result.get("error")}')
            return None
            
    except Exception as e:
        emit_status(session_id, 'error', f'❌ {phase_name} error: {str(e)}')
        return None


def analyze_repository_async(github_url, session_id, user_env_vars=None, github_token=None):
    """Analyze repository asynchronously with optional GitHub token for private repos"""
    try:
        # Initialize analysis session
        analysis_sessions[session_id] = {
            'github_url': github_url,
            'status': 'started',
            'start_time': datetime.now(),
            'user_env_vars': user_env_vars or {},
            'github_token': github_token  # Store token for repository access
        }
        
        # Emit start event
        socketio.emit('analysis_update', {
            'status': 'started',
            'message': 'Starting repository analysis...',
            'timestamp': datetime.now().isoformat()
        }, room=session_id)
        
        # Prepare context for user-provided environment variables
        env_vars_context = ""
        if user_env_vars:
            env_vars_list = [f"- {key}={value}" for key, value in user_env_vars.items()]
            env_vars_context = f"""
USER PROVIDED ENVIRONMENT VARIABLES:
{chr(10).join(env_vars_list)}

These environment variables should be considered when analyzing deployment feasibility.
"""
        
        # Clone repository with authentication if token provided
        local_path = clone_repository_with_auth(github_url, github_token)
        
        if not local_path:
            raise Exception("Failed to clone repository")
        
        try:
            # Get repository structure and content
            repo_structure = get_repository_structure(local_path)
            repo_content = get_repository_content(local_path)
            
            # Create comprehensive analysis context
            analysis_context = f"""
REPOSITORY: {github_url}
STRUCTURE:
{repo_structure}

CONTENT ANALYSIS:
{repo_content}

{env_vars_context}
"""
            
            # Perform initial analysis
            socketio.emit('analysis_update', {
                'status': 'processing',
                'message': 'Analyzing repository structure and dependencies...',
                'timestamp': datetime.now().isoformat()
            }, room=session_id)
            
            initial_prompt = f"""Analyze this GitHub repository for deployment feasibility: {github_url}

{env_vars_context}

Focus on critical deployment blockers. Give a preliminary assessment and identify if any essential information is missing that would prevent giving a definitive YES/NO answer.

Consider these factors:
- Application structure and entry points
- Dependency management
- Configuration requirements (considering user-provided env vars)
- Hardcoded values that prevent deployment
- Missing essential configurations not provided by user

Provide a structured analysis with clear reasoning.

REPOSITORY ANALYSIS:
{analysis_context}
"""
            
            initial_response = agent_instance.ask_question(initial_prompt)
            
            if not initial_response.get("success"):
                raise Exception(f"Initial analysis failed: {initial_response.get('error')}")
                
            initial_result = initial_response["answer"]
            
            # Store initial analysis
            analysis_sessions[session_id]['initial_analysis'] = initial_result
            
            # Emit phase complete
            socketio.emit('analysis_update', {
                'status': 'phase_complete',
                'data': {
                    'phase': 'initial',
                    'result': initial_result
                },
                'message': 'Initial analysis complete',
                'timestamp': datetime.now().isoformat()
            }, room=session_id)
            
            # Check if we need to ask questions
            if should_ask_questions(initial_result, user_env_vars):
                # Generate minimal questions
                questions_prompt = f"""Based on this analysis, generate ONLY the most critical questions (maximum 3) needed to determine deployment feasibility:

{initial_result}

USER PROVIDED ENVIRONMENT VARIABLES:
{env_vars_context}

Only ask about information that is:
1. Absolutely essential for deployment
2. Not already provided by the user's environment variables
3. Cannot be reasonably inferred from the repository

Format as numbered questions."""
                
                questions_response = agent_instance.ask_question(questions_prompt)
                
                if not questions_response.get("success"):
                    raise Exception(f"Questions generation failed: {questions_response.get('error')}")
                
                questions = questions_response["answer"]
                
                analysis_sessions[session_id]['questions'] = questions
                
                socketio.emit('analysis_update', {
                    'status': 'questions_ready',
                    'data': {
                        'questions': questions
                    },
                    'message': 'Questions generated - waiting for user input',
                    'timestamp': datetime.now().isoformat()
                }, room=session_id)
                
            else:
                # Generate final assessment directly
                final_assessment = generate_final_assessment_content(
                    initial_result, 
                    [], 
                    user_env_vars, 
                    github_url
                )
                
                analysis_sessions[session_id]['final_assessment'] = final_assessment
                
                socketio.emit('analysis_update', {
                    'status': 'completed',
                    'data': {
                        'final_assessment': final_assessment
                    },
                    'message': 'Analysis complete!',
                    'timestamp': datetime.now().isoformat()
                }, room=session_id)
                
        finally:
            # Clean up repository
            cleanup_repository(local_path)
            
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        socketio.emit('analysis_update', {
            'status': 'error',
            'message': f'Analysis failed: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }, room=session_id)


def generate_final_assessment_content(initial_analysis, user_responses, user_env_vars, github_url):
    """Generate the final assessment content."""
    # Prepare environment variables for deployment instructions
    env_vars_section = ""
    if user_env_vars:
        env_vars_section = f"""
        
**USER PROVIDED ENVIRONMENT VARIABLES:**
Create a .env file with these variables:
```
{chr(10).join([f"{key}={value}" for key, value in user_env_vars.items()])}
```
"""
    
    final_prompt = f"""
    Based on the repository analysis of {github_url} and user responses, provide a final simple assessment.
    
    Original Analysis:
    {initial_analysis}
    
    User-Provided Environment Variables:
    {chr(10).join([f"- {key}={value}" for key, value in user_env_vars.items()]) if user_env_vars else "None provided"}
    
    User Responses:
    {chr(10).join([f"Q: {resp['question']} | A: {resp['answer']}" for resp in user_responses])}
    
    Provide a SIMPLE final assessment:
    
    ## CAN THIS REPOSITORY BE DEPLOYED?
    
    **ANSWER: YES/NO**
    
    **REASON:**
    - If NO: Clearly explain what prevents deployment (hardcoded localhost, missing critical files, etc.)
    - If YES: Brief explanation of why it's deployable, mention user-provided environment variables if relevant
    
    ## DEPLOYMENT SETUP (only if deployable)
    If YES, provide simple setup instructions:
    
    **PREREQUISITES:**
    - List what's needed (Node.js, Python, database, etc.)
    
    **SETUP STEPS:**
    1. Clone the repository
    2. Install dependencies
    3. Create environment file with provided variables
    4. Set up database (if needed)
    5. Run the application
    
    **ENVIRONMENT VARIABLES:**
    {env_vars_section}
    - Add any additional required variables not provided by user
    
    **HOW TO RUN:**
    - Command to start the application
    - Port it will run on (use user-provided PORT if available, otherwise default)
    - How to access it
    
    **DEPLOYMENT COMMAND:**
    Provide the exact .env file content and run commands based on user's environment variables.
    
    Keep it simple and practical - focus on what the user needs to do to deploy this with their provided environment variables.
    """
    
    response = agent_instance.ask_question(final_prompt)
    
    if response.get("success"):
        return response["answer"]
    else:
        raise Exception(f"Final assessment failed: {response.get('error')}")


def generate_final_assessment(session_id):
    """Generate final simple deployment assessment."""
    try:
        session = analysis_sessions[session_id]
        github_url = session['github_url']
        user_env_vars = session.get('user_env_vars', {})
        initial_analysis = session['initial_analysis']
        user_responses = session.get('user_responses', [])
        
        final_assessment = generate_final_assessment_content(
            initial_analysis, 
            user_responses, 
            user_env_vars, 
            github_url
        )
        
        analysis_sessions[session_id]['final_assessment'] = final_assessment
        analysis_sessions[session_id]['status'] = 'completed'
        analysis_sessions[session_id]['end_time'] = datetime.now()
        
        emit_status(session_id, 'completed', '🎉 Analysis completed!', {
            'final_assessment': final_assessment,
            'user_env_vars': user_env_vars
        })
            
    except Exception as e:
        emit_status(session_id, 'error', f'❌ Final assessment failed: {str(e)}')
        analysis_sessions[session_id]['status'] = 'failed'


@app.route('/')
def index():
    """Main page."""
    return render_template('index.html')


@app.route('/api/health')
def health_check():
    """Health check endpoint."""
    api_key = os.getenv("OPENROUTER_API_KEY")
    return jsonify({
        'status': 'healthy',
        'api_key_configured': bool(api_key),
        'agent_ready': agent_instance is not None
    })


@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    print(f"Client connected: {request.sid}")
    emit('connected', {'session_id': request.sid})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    print(f"Client disconnected: {request.sid}")
    # Clean up session data if needed
    if request.sid in analysis_sessions:
        del analysis_sessions[request.sid]


@socketio.on('start_analysis')
def handle_start_analysis(data):
    """Start repository analysis."""
    github_url = data.get('github_url')
    user_env_vars = data.get('user_env_vars', {})
    github_token = data.get('github_token')  # Optional GitHub token for private repos
    
    if not github_url:
        emit('error', {'message': 'GitHub URL is required'})
        return
    
    session_id = request.sid
    
    # Start analysis in background thread
    socketio.start_background_task(
        analyze_repository_async, 
        github_url, 
        session_id, 
        user_env_vars,
        github_token
    )


@socketio.on('submit_responses')
def handle_submit_responses(data):
    """Handle user responses to questions."""
    session_id = request.sid
    responses = data.get('responses', [])
    
    if session_id not in analysis_sessions:
        emit('error', {'message': 'No active analysis session found'})
        return
    
    # Store user responses
    analysis_sessions[session_id]['user_responses'] = responses
    analysis_sessions[session_id]['status'] = 'generating_final'
    
    # Generate final assessment in background thread
    thread = threading.Thread(target=generate_final_assessment, args=(session_id,))
    thread.daemon = True
    thread.start()


@socketio.on('get_session_status')
def handle_get_session_status():
    """Get current session status."""
    session_id = request.sid
    if session_id in analysis_sessions:
        session = analysis_sessions[session_id]
        emit('session_status', {
            'status': session['status'],
            'github_url': session.get('github_url'),
            'phases': list(session.get('phases', {}).keys())
        })
    else:
        emit('session_status', {'status': 'none'})


if __name__ == '__main__':
    # Initialize agent on startup
    if initialize_agent():
        print("✅ Agent initialized successfully!")
    else:
        print("⚠️ Warning: API key not found. Please configure OPENROUTER_API_KEY in .env")
    
    print("🚀 Starting GitHub Repository Deployment Analyzer...")
    print("📱 Open your browser and go to: http://localhost:5000")
    
    socketio.run(app, debug=True, host='0.0.0.0', port=5000) 