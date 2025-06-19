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


def analyze_repository_async(session_id, github_url, user_env_vars=None):
    """Run the simplified repository analysis."""
    try:
        analysis_sessions[session_id] = {
            'status': 'running',
            'github_url': github_url,
            'user_env_vars': user_env_vars or {},
            'phases': {},
            'user_responses': [],
            'start_time': datetime.now()
        }
        
        emit_status(session_id, 'started', f'🚀 Starting analysis of {github_url}')
        
        # Prepare environment variables context
        env_vars_context = ""
        if user_env_vars:
            env_vars_context = f"""
            
## USER PROVIDED ENVIRONMENT VARIABLES
The user has provided these environment variables for deployment:
{chr(10).join([f"- {key}={value}" for key, value in user_env_vars.items()])}

Use these in your deployment analysis and setup instructions.
"""
        
        # Phase 1: Check Deployability
        initial_prompt = f"""
        Analyze the GitHub repository: {github_url} to determine if it can be deployed.
        {env_vars_context}
        
        Focus ONLY on critical deployment blockers:

        ## CRITICAL CHECKS
        1. **Hardcoded Issues**:
           - Hardcoded localhost URLs (localhost, 127.0.0.1, http://localhost:3000, etc.)
           - Hardcoded file paths that won't work in production
           - Development-only configurations that prevent deployment

        2. **Missing Essential Files**:
           - No application code (just README files)
           - Missing main entry point files
           - No deployment configuration at all

        3. **Configuration Issues**:
           - Required environment variables that are completely missing (consider user-provided vars)
           - Database configurations that are incomplete
           - Missing critical dependencies

        ## ANALYSIS RESULT
        Provide a clear assessment in this format:

        **DEPLOYABLE: YES/NO**

        **REASON:**
        - If NO: List the specific blockers (hardcoded localhost, missing files, etc.)
        - If YES: Mention what makes it deployable, including user-provided environment variables

        **MISSING INFO NEEDED:**
        - Only list truly essential missing information that prevents deployment
        - Consider the user-provided environment variables when determining missing info
        - Don't ask for optional configurations
        - Keep it minimal - only critical missing pieces

        Clone the repository, examine the code, and provide this simple assessment.
        Clean up after analysis.
        """
        
        phase1_result = run_analysis_phase(session_id, github_url, 'initial', initial_prompt, 'Checking Deployability')
        
        if not phase1_result:
            analysis_sessions[session_id]['status'] = 'failed'
            return
        
        analysis_sessions[session_id]['phases']['initial'] = phase1_result['answer']
        
        # Check if we need to ask questions
        analysis_text = phase1_result['answer'].lower()
        if 'missing info needed:' in analysis_text and len(analysis_text.split('missing info needed:')[1].strip()) > 10:
            # Phase 2: Generate minimal questions
            questions_prompt = f"""
            Based on the analysis, create MINIMAL questions only for truly critical missing information.
            
            Previous analysis:
            {phase1_result['answer']}
            
            User-provided environment variables:
            {chr(10).join([f"- {key}={value}" for key, value in user_env_vars.items()]) if user_env_vars else "None provided"}
            
            Create questions ONLY if there are critical missing pieces that prevent deployment.
            Consider the user-provided environment variables - don't ask for information they already provided.
            Focus on:
            - Essential environment variables that are required but not provided by user
            - Critical database/service configurations not covered by user env vars
            - Missing deployment information that blocks hosting
            
            If no critical information is missing, return "NO QUESTIONS NEEDED"
            
            If questions are needed, format as a simple numbered list:
            1. Question about critical missing item
            2. Another critical question (if needed)
            
            Keep it minimal - maximum 3 questions.
            """
            
            questions_result = run_analysis_phase(session_id, github_url, 'questions', questions_prompt, 'Checking for Missing Info')
            
            if questions_result and 'NO QUESTIONS NEEDED' not in questions_result['answer'].upper():
                analysis_sessions[session_id]['phases']['questions'] = questions_result['answer']
                analysis_sessions[session_id]['status'] = 'awaiting_user_input'
                
                emit_status(session_id, 'questions_ready', '💬 Need some missing information', {
                    'questions': questions_result['answer']
                })
            else:
                # No questions needed, go directly to final
                generate_final_assessment(session_id)
        else:
            # No missing info, go directly to final
            generate_final_assessment(session_id)
            
    except Exception as e:
        emit_status(session_id, 'error', f'❌ Analysis failed: {str(e)}')
        analysis_sessions[session_id]['status'] = 'failed'


def generate_final_assessment(session_id):
    """Generate final simple deployment assessment."""
    try:
        session = analysis_sessions[session_id]
        github_url = session['github_url']
        user_env_vars = session.get('user_env_vars', {})
        initial_analysis = session['phases'].get('initial', '')
        user_responses = session.get('user_responses', [])
        
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
        
        final_result = run_analysis_phase(session_id, github_url, 'final', final_prompt, 'Final Assessment')
        
        if final_result:
            analysis_sessions[session_id]['phases']['final'] = final_result['answer']
            analysis_sessions[session_id]['status'] = 'completed'
            analysis_sessions[session_id]['end_time'] = datetime.now()
            
            emit_status(session_id, 'completed', '🎉 Analysis completed!', {
                'final_assessment': final_result['answer'],
                'model_used': final_result.get('model_used', 'Unknown'),
                'user_env_vars': user_env_vars
            })
        else:
            analysis_sessions[session_id]['status'] = 'failed'
            
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
    session_id = request.sid
    github_url = data.get('github_url', '').strip()
    user_env_vars = data.get('user_env_vars', {})
    
    # Validate URL
    if not github_url.startswith('https://github.com/'):
        emit('error', {'message': 'Please provide a valid GitHub URL (should start with https://github.com/)'})
        return
    
    # Check if agent is initialized
    if not agent_instance:
        if not initialize_agent():
            emit('error', {'message': 'API key not configured. Please check your .env file.'})
            return
    
    # Start analysis in background thread
    thread = threading.Thread(target=analyze_repository_async, args=(session_id, github_url, user_env_vars))
    thread.daemon = True
    thread.start()


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