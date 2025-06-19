/**
 * GitHub Repository Deployment Analyzer - Simplified Frontend
 * Simple YES/NO deployment analysis with minimal questions
 */

class DeploymentAnalyzer {
    constructor() {
        this.socket = null;
        this.sessionId = null;
        this.analysisStartTime = null;
        this.timerInterval = null;
        this.currentPhase = 0;
        this.questions = [];
        this.userEnvVars = {};
        this.customEnvCounter = 0;
        this.githubToken = null;
        this.githubUser = null;
        this.repositories = [];
        this.selectedRepo = null;
        this.currentTab = 'public';
        
        this.init();
    }
    
    init() {
        this.initializeSocket();
        this.attachEventListeners();
        this.checkAPIStatus();
    }
    
    initializeSocket() {
        this.socket = io();
        
        this.socket.on('connect', () => {
            console.log('Connected to server');
            this.updateConnectionStatus(true);
        });
        
        this.socket.on('disconnect', () => {
            console.log('Disconnected from server');
            this.updateConnectionStatus(false);
        });
        
        this.socket.on('connected', (data) => {
            this.sessionId = data.session_id;
            console.log('Session ID:', this.sessionId);
        });
        
        this.socket.on('analysis_update', (data) => {
            this.handleAnalysisUpdate(data);
        });
        
        this.socket.on('error', (data) => {
            this.showError(data.message);
        });
    }
    
    attachEventListeners() {
        // Tab switching
        const tabPublic = document.getElementById('tab-public');
        if (tabPublic) {
            tabPublic.addEventListener('click', () => {
                this.switchTab('public');
            });
        }

        const tabPrivate = document.getElementById('tab-private');
        if (tabPrivate) {
            tabPrivate.addEventListener('click', () => {
                this.switchTab('private');
            });
        }

        // Check button - now shows env vars section
        const analyzeBtn = document.getElementById('analyze-btn');
        if (analyzeBtn) {
            analyzeBtn.addEventListener('click', () => {
                this.showEnvVarsSection();
            });
        }

        // Enter key on URL input
        const githubUrl = document.getElementById('github-url');
        if (githubUrl) {
            githubUrl.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.showEnvVarsSection();
                }
            });
        }

        // Example URL buttons
        document.querySelectorAll('.example-url').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const url = e.target.getAttribute('data-url');
                const urlInput = document.getElementById('github-url');
                if (urlInput) {
                    urlInput.value = url;
                }
            });
        });

        // GitHub Authentication
        const connectGithubBtn = document.getElementById('connect-github-btn');
        if (connectGithubBtn) {
            connectGithubBtn.addEventListener('click', () => {
                this.connectGitHub();
            });
        }

        const disconnectGithub = document.getElementById('disconnect-github');
        if (disconnectGithub) {
            disconnectGithub.addEventListener('click', () => {
                this.disconnectGitHub();
            });
        }

        // GitHub token input
        const githubToken = document.getElementById('github-token');
        if (githubToken) {
            githubToken.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.connectGitHub();
                }
            });
        }

        // Repository search
        const repoSearch = document.getElementById('repo-search');
        if (repoSearch) {
            repoSearch.addEventListener('input', (e) => {
                this.filterRepositories(e.target.value);
            });
        }

        // Private repository analysis
        const analyzePrivateBtn = document.getElementById('analyze-private-btn');
        if (analyzePrivateBtn) {
            analyzePrivateBtn.addEventListener('click', () => {
                this.analyzePrivateRepo();
            });
        }

        // Environment variables section
        const addEnvVar = document.getElementById('add-env-var');
        if (addEnvVar) {
            addEnvVar.addEventListener('click', () => {
                this.addCustomEnvVar();
            });
        }

        const skipEnvVars = document.getElementById('skip-env-vars');
        if (skipEnvVars) {
            skipEnvVars.addEventListener('click', () => {
                this.startAnalysis();
            });
        }

        const submitEnvVars = document.getElementById('submit-env-vars');
        if (submitEnvVars) {
            submitEnvVars.addEventListener('click', () => {
                this.collectEnvVarsAndAnalyze();
            });
        }

        // Full .env file content handling
        const fullEnvContent = document.getElementById('full-env-content');
        if (fullEnvContent) {
            fullEnvContent.addEventListener('input', () => {
                this.handleFullEnvInput();
            });
        }

        const clearEnvContent = document.getElementById('clear-env-content');
        if (clearEnvContent) {
            clearEnvContent.addEventListener('click', () => {
                this.clearAllEnvInputs();
            });
        }

        // Environment variables input listeners
        this.attachEnvVarListeners();

        // Submit responses button
        const submitResponses = document.getElementById('submit-responses');
        if (submitResponses) {
            submitResponses.addEventListener('click', () => {
                this.submitResponses();
            });
        }

        // New analysis button
        const newAnalysis = document.getElementById('new-analysis');
        if (newAnalysis) {
            newAnalysis.addEventListener('click', () => {
                this.resetAnalysis();
            });
        }
    }
    
    attachEnvVarListeners() {
        // Listen to common env var inputs
        const envInputs = [
            'env-database-url', 'env-db-host', 'env-db-port',
            'env-secret-key', 'env-api-keys', 'env-port'
        ];
        
        envInputs.forEach(id => {
            const input = document.getElementById(id);
            if (input) {
                input.addEventListener('input', () => {
                    this.handleFormInputChange();
                });
            }
        });
    }
    
    async checkAPIStatus() {
        try {
            const response = await fetch('/api/health');
            const data = await response.json();
            
            const statusElement = document.getElementById('api-status');
            if (data.api_key_configured && data.agent_ready) {
                statusElement.textContent = '✅ API Ready';
                statusElement.className = 'text-sm text-green-400 mt-1';
            } else if (data.api_key_configured) {
                statusElement.textContent = '⚠️ API Key Found, Initializing...';
                statusElement.className = 'text-sm text-yellow-400 mt-1';
            } else {
                statusElement.textContent = '❌ API Key Missing';
                statusElement.className = 'text-sm text-red-400 mt-1';
            }
        } catch (error) {
            console.error('Failed to check API status:', error);
            document.getElementById('api-status').textContent = '❌ API Check Failed';
        }
    }
    
    updateConnectionStatus(connected) {
        const statusElement = document.getElementById('connection-status');
        if (!statusElement) {
            console.warn('connection-status element not found');
            return;
        }
        
        const indicator = statusElement.querySelector('div');
        const text = statusElement.querySelector('span');
        
        if (indicator && text) {
            if (connected) {
                indicator.className = 'w-3 h-3 bg-green-400 rounded-full animate-pulse';
                text.textContent = 'Connected';
            } else {
                indicator.className = 'w-3 h-3 bg-red-400 rounded-full';
                text.textContent = 'Disconnected';
            }
        }
    }
    
    switchTab(tab) {
        this.currentTab = tab;
        
        // Update tab buttons
        document.querySelectorAll('.tab-button').forEach(btn => {
            btn.classList.remove('active');
        });
        document.getElementById(`tab-${tab}`).classList.add('active');
        
        // Show/hide content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.add('hidden');
        });
        document.getElementById(`${tab}-repo-section`).classList.remove('hidden');
        
        // Reset selections
        this.resetSelections();
    }
    
    resetSelections() {
        // Clear URL input
        const githubUrl = document.getElementById('github-url');
        if (githubUrl) {
            githubUrl.value = '';
        }
        
        // Reset selected repository
        this.selectedRepo = null;
        const selectedRepoInfo = document.getElementById('selected-repo-info');
        if (selectedRepoInfo) {
            selectedRepoInfo.classList.add('hidden');
        }
        
        // Clear search
        const searchInput = document.getElementById('repo-search');
        if (searchInput) {
            searchInput.value = '';
        }
    }
    
    async connectGitHub() {
        const tokenInput = document.getElementById('github-token');
        if (!tokenInput) {
            this.showError('GitHub token input not found');
            return;
        }
        
        const token = tokenInput.value.trim();
        
        if (!token) {
            this.showError('Please enter your GitHub Personal Access Token');
            return;
        }
        
        if (!token.startsWith('ghp_') && !token.startsWith('github_pat_')) {
            this.showError('Please enter a valid GitHub Personal Access Token');
            return;
        }
        
        const connectBtn = document.getElementById('connect-github-btn');
        if (connectBtn) {
            connectBtn.disabled = true;
            connectBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Connecting...';
        }
        
        try {
            // Verify token and get user info
            const userResponse = await fetch('https://api.github.com/user', {
                headers: {
                    'Authorization': `token ${token}`,
                    'Accept': 'application/vnd.github.v3+json'
                }
            });
            
            if (!userResponse.ok) {
                throw new Error('Invalid token or insufficient permissions');
            }
            
            const userData = await userResponse.json();
            this.githubToken = token;
            this.githubUser = userData;
            
            // Show user info and repository selection
            this.showGitHubUserInfo(userData);
            await this.fetchRepositories();
            
        } catch (error) {
            this.showError(`Failed to connect to GitHub: ${error.message}`);
            if (connectBtn) {
                connectBtn.disabled = false;
                connectBtn.innerHTML = '<i class="fab fa-github mr-2"></i>Connect GitHub Account';
            }
        }
    }
    
    showGitHubUserInfo(user) {
        // Hide auth section, show repo selection
        const authSection = document.getElementById('github-auth-section');
        if (authSection) {
            authSection.classList.add('hidden');
        }
        
        const repoSection = document.getElementById('repo-selection-section');
        if (repoSection) {
            repoSection.classList.remove('hidden');
        }
        
        // Update user info
        const userAvatar = document.getElementById('user-avatar');
        if (userAvatar) {
            userAvatar.src = user.avatar_url;
        }
        
        const userName = document.getElementById('user-name');
        if (userName) {
            userName.textContent = user.name || user.login;
        }
        
        const userLogin = document.getElementById('user-login');
        if (userLogin) {
            userLogin.textContent = `@${user.login}`;
        }
    }
    
    async fetchRepositories() {
        try {
            const loadingElement = document.getElementById('repos-loading');
            if (loadingElement) {
                loadingElement.style.display = 'block';
            }
            
            // Fetch user's repositories
            const reposResponse = await fetch('https://api.github.com/user/repos?sort=updated&per_page=100', {
                headers: {
                    'Authorization': `token ${this.githubToken}`,
                    'Accept': 'application/vnd.github.v3+json'
                }
            });
            
            if (!reposResponse.ok) {
                throw new Error('Failed to fetch repositories');
            }
            
            const repos = await reposResponse.json();
            this.repositories = repos;
            
            this.displayRepositories(repos);
            
        } catch (error) {
            this.showError(`Failed to fetch repositories: ${error.message}`);
        } finally {
            const loadingElement = document.getElementById('repos-loading');
            if (loadingElement) {
                loadingElement.style.display = 'none';
            }
        }
    }
    
    displayRepositories(repos) {
        const container = document.getElementById('repositories-container');
        if (!container) {
            console.error('repositories-container not found');
            return;
        }
        
        // Clear loading state
        container.innerHTML = '';
        
        if (repos.length === 0) {
            container.innerHTML = `
                <div class="p-8 text-center text-gray-500">
                    <i class="fas fa-folder-open text-2xl mb-2"></i>
                    <p>No repositories found</p>
                </div>
            `;
            return;
        }
        
        repos.forEach(repo => {
            const repoItem = this.createRepositoryItem(repo);
            container.appendChild(repoItem);
        });
    }
    
    createRepositoryItem(repo) {
        const item = document.createElement('div');
        item.className = 'repo-item p-4 border-b border-gray-200 hover:bg-gray-50';
        item.dataset.repoId = repo.id;
        
        const languageClass = repo.language ? 
            `lang-${repo.language.toLowerCase()}` : 'lang-default';
        
        const updatedDate = new Date(repo.updated_at).toLocaleDateString();
        
        item.innerHTML = `
            <div class="flex items-center justify-between">
                <div class="flex-1">
                    <div class="flex items-center space-x-2 mb-1">
                        <span class="repo-language ${languageClass}"></span>
                        <h4 class="font-semibold text-gray-800">${repo.name}</h4>
                        ${repo.private ? '<i class="fas fa-lock text-gray-400 text-xs"></i>' : '<i class="fas fa-globe text-gray-400 text-xs"></i>'}
                    </div>
                    <p class="text-sm text-gray-600 mb-2">${repo.description || 'No description'}</p>
                    <div class="flex items-center space-x-4 text-xs text-gray-500">
                        ${repo.language ? `<span><i class="fas fa-code mr-1"></i>${repo.language}</span>` : ''}
                        <span><i class="fas fa-star mr-1"></i>${repo.stargazers_count}</span>
                        <span><i class="fas fa-code-branch mr-1"></i>${repo.forks_count}</span>
                        <span><i class="fas fa-clock mr-1"></i>Updated ${updatedDate}</span>
                    </div>
                </div>
                <div class="ml-4">
                    <button class="select-repo-btn px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded hover:bg-blue-200 transition-colors">
                        Select
                    </button>
                </div>
            </div>
        `;
        
        // Add click handler
        item.addEventListener('click', () => {
            this.selectRepository(repo);
        });
        
        return item;
    }
    
    selectRepository(repo) {
        this.selectedRepo = repo;
        
        // Update UI
        document.querySelectorAll('.repo-item').forEach(item => {
            item.classList.remove('selected');
        });
        
        const selectedItem = document.querySelector(`[data-repo-id="${repo.id}"]`);
        if (selectedItem) {
            selectedItem.classList.add('selected');
        }
        
        // Show selected repo info
        const selectedRepoName = document.getElementById('selected-repo-name');
        if (selectedRepoName) {
            selectedRepoName.textContent = repo.full_name;
        }
        
        const selectedRepoDescription = document.getElementById('selected-repo-description');
        if (selectedRepoDescription) {
            selectedRepoDescription.textContent = repo.description || 'No description available';
        }
        
        const selectedRepoInfo = document.getElementById('selected-repo-info');
        if (selectedRepoInfo) {
            selectedRepoInfo.classList.remove('hidden');
        }
    }
    
    filterRepositories(searchTerm) {
        const filteredRepos = this.repositories.filter(repo => 
            repo.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
            (repo.description && repo.description.toLowerCase().includes(searchTerm.toLowerCase()))
        );
        
        this.displayRepositories(filteredRepos);
    }
    
    disconnectGitHub() {
        // Reset GitHub state
        this.githubToken = null;
        this.githubUser = null;
        this.repositories = [];
        this.selectedRepo = null;
        
        // Reset UI
        document.getElementById('github-auth-section').classList.remove('hidden');
        document.getElementById('repo-selection-section').classList.add('hidden');
        document.getElementById('github-token').value = '';
        document.getElementById('selected-repo-info').classList.add('hidden');
        
        // Reset connect button
        const connectBtn = document.getElementById('connect-github-btn');
        connectBtn.disabled = false;
        connectBtn.innerHTML = '<i class="fab fa-github mr-2"></i>Connect GitHub Account';
    }
    
    analyzePrivateRepo() {
        if (!this.selectedRepo) {
            this.showError('Please select a repository first');
            return;
        }
        
        // Set the repository URL for analysis
        const repoUrl = this.selectedRepo.html_url;
        
        // Store the GitHub token for the analysis
        this.currentRepoToken = this.githubToken;
        this.currentRepoUrl = repoUrl;
        
        // Show environment variables section
        this.showEnvVarsSection(true);
    }
    
    showEnvVarsSection(isPrivate = false) {
        let githubUrl;
        
        if (isPrivate) {
            // Using private repository
            githubUrl = this.currentRepoUrl;
        } else {
            // Using public repository
            githubUrl = document.getElementById('github-url').value.trim();
            
            if (!githubUrl) {
                this.showError('Please enter a GitHub repository URL');
                return;
            }
            
            if (!githubUrl.startsWith('https://github.com/')) {
                this.showError('Please enter a valid GitHub URL (should start with https://github.com/)');
                return;
            }
        }
        
        // Show environment variables section
        document.getElementById('env-vars-section').classList.remove('hidden');
        document.getElementById('env-vars-section').scrollIntoView({ behavior: 'smooth' });
        
        // Update preview
        this.updateEnvPreview();
    }
    
    addCustomEnvVar() {
        this.customEnvCounter++;
        const container = document.getElementById('custom-env-vars');
        
        const envVarDiv = document.createElement('div');
        envVarDiv.className = 'flex space-x-3 items-center';
        envVarDiv.id = `custom-env-${this.customEnvCounter}`;
        
        envVarDiv.innerHTML = `
            <div class="flex-1">
                <input type="text" placeholder="VARIABLE_NAME" 
                       class="custom-env-key w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-purple-500">
            </div>
            <div class="flex-1">
                <input type="text" placeholder="variable_value" 
                       class="custom-env-value w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-purple-500">
            </div>
            <button class="remove-env-var px-3 py-2 text-red-600 hover:bg-red-50 rounded-md transition-colors">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        container.appendChild(envVarDiv);
        
        // Add event listeners
        const keyInput = envVarDiv.querySelector('.custom-env-key');
        const valueInput = envVarDiv.querySelector('.custom-env-value');
        const removeBtn = envVarDiv.querySelector('.remove-env-var');
        
        keyInput.addEventListener('input', () => this.updateEnvPreview());
        valueInput.addEventListener('input', () => this.updateEnvPreview());
        removeBtn.addEventListener('click', () => {
            envVarDiv.remove();
            this.updateEnvPreview();
        });
        
        // Focus on the new input
        keyInput.focus();
    }
    
    updateEnvPreview() {
        const envVars = this.collectEnvVars();
        const preview = document.getElementById('env-preview');
        
        let envContent = '# Environment Variables for Deployment\n\n';
        
        if (Object.keys(envVars).length === 0) {
            envContent += '# No environment variables specified\n# You can add them above or skip this step';
        } else {
            Object.entries(envVars).forEach(([key, value]) => {
                if (key && value) {
                    envContent += `${key}=${value}\n`;
                }
            });
        }
        
        preview.textContent = envContent;
    }
    
    handleFullEnvInput() {
        const fullEnvContent = document.getElementById('full-env-content').value;
        
        if (fullEnvContent.trim()) {
            // Parse the .env content and populate individual fields
            this.parseAndPopulateEnvVars(fullEnvContent);
            
            // Clear individual form inputs since we're using the full content
            this.clearFormInputs();
            
            // Update preview with full content
            this.updateEnvPreviewFromFullContent(fullEnvContent);
        } else {
            // If full content is cleared, update preview from form inputs
            this.updateEnvPreview();
        }
    }
    
    handleFormInputChange() {
        // Only update if full env content is empty
        const fullEnvContent = document.getElementById('full-env-content').value.trim();
        if (!fullEnvContent) {
            this.updateEnvPreview();
        }
    }
    
    parseAndPopulateEnvVars(envContent) {
        // This function parses .env content but doesn't populate individual form fields
        // Instead, we'll use the full content directly
        // This keeps the original .env format intact
    }
    
    clearFormInputs() {
        // Clear individual form inputs when using full .env content
        const envInputs = [
            'env-database-url', 'env-db-host', 'env-db-port',
            'env-secret-key', 'env-api-keys', 'env-port'
        ];
        
        envInputs.forEach(id => {
            const input = document.getElementById(id);
            if (input) {
                input.value = '';
            }
        });
        
        // Clear custom env vars
        document.getElementById('custom-env-vars').innerHTML = '';
    }
    
    clearAllEnvInputs() {
        // Clear the full env content
        document.getElementById('full-env-content').value = '';
        
        // Clear individual form inputs
        this.clearFormInputs();
        
        // Reset custom env counter
        this.customEnvCounter = 0;
        
        // Update preview
        this.updateEnvPreview();
    }
    
    updateEnvPreviewFromFullContent(fullEnvContent) {
        const preview = document.getElementById('env-preview');
        
        if (fullEnvContent.trim()) {
            // Clean up the content - remove empty lines and format nicely
            const lines = fullEnvContent.split('\n');
            const cleanedLines = lines.map(line => line.trim()).filter(line => line);
            const formattedContent = '# Environment Variables for Deployment\n\n' + cleanedLines.join('\n');
            
            preview.textContent = formattedContent;
        } else {
            preview.textContent = '# Your environment variables will appear here';
        }
    }
    
    collectEnvVars() {
        const envVars = {};
        
        // First check if there's full .env content
        const fullEnvContent = document.getElementById('full-env-content').value.trim();
        
        if (fullEnvContent) {
            // Parse the full .env content
            const lines = fullEnvContent.split('\n');
            
            lines.forEach(line => {
                const trimmedLine = line.trim();
                
                // Skip empty lines and comments
                if (!trimmedLine || trimmedLine.startsWith('#')) {
                    return;
                }
                
                // Parse KEY=VALUE format
                const equalIndex = trimmedLine.indexOf('=');
                if (equalIndex > 0) {
                    const key = trimmedLine.substring(0, equalIndex).trim();
                    const value = trimmedLine.substring(equalIndex + 1).trim();
                    
                    // Remove quotes if present
                    const cleanValue = value.replace(/^["']|["']$/g, '');
                    
                    if (key && cleanValue) {
                        envVars[key] = cleanValue;
                    }
                }
            });
            
            return envVars;
        }
        
        // If no full content, collect from individual form inputs
        // Collect common env vars
        const commonVars = {
            'DATABASE_URL': document.getElementById('env-database-url')?.value.trim(),
            'DB_HOST': document.getElementById('env-db-host')?.value.trim(),
            'DB_PORT': document.getElementById('env-db-port')?.value.trim(),
            'SECRET_KEY': document.getElementById('env-secret-key')?.value.trim(),
            'PORT': document.getElementById('env-port')?.value.trim()
        };
        
        // Add common vars if they have values
        Object.entries(commonVars).forEach(([key, value]) => {
            if (value) {
                envVars[key] = value;
            }
        });
        
        // Handle API keys (comma-separated)
        const apiKeys = document.getElementById('env-api-keys')?.value.trim();
        if (apiKeys) {
            apiKeys.split(',').forEach(keyPair => {
                const [key, value] = keyPair.split('=').map(s => s.trim());
                if (key && value) {
                    envVars[key] = value;
                }
            });
        }
        
        // Collect custom env vars
        document.querySelectorAll('#custom-env-vars > div').forEach(div => {
            const key = div.querySelector('.custom-env-key')?.value.trim();
            const value = div.querySelector('.custom-env-value')?.value.trim();
            if (key && value) {
                envVars[key] = value;
            }
        });
        
        return envVars;
    }
    
    collectEnvVarsAndAnalyze() {
        this.userEnvVars = this.collectEnvVars();
        console.log('Collected environment variables:', this.userEnvVars);
        
        // Hide env vars section
        document.getElementById('env-vars-section').classList.add('hidden');
        
        // Start analysis with env vars
        this.startAnalysis();
    }
    
    startAnalysis() {
        let githubUrl;
        let githubToken = null;
        
        if (this.currentTab === 'private' && this.selectedRepo) {
            // Using private repository
            githubUrl = this.currentRepoUrl;
            githubToken = this.currentRepoToken;
        } else {
            // Using public repository
            githubUrl = document.getElementById('github-url').value.trim();
            
            if (!githubUrl) {
                this.showError('Please enter a GitHub repository URL');
                return;
            }
            
            if (!githubUrl.startsWith('https://github.com/')) {
                this.showError('Please enter a valid GitHub URL (should start with https://github.com/)');
                return;
            }
        }
        
        // Reset UI state
        this.resetAnalysisState();
        
        // Show analysis section
        document.getElementById('analysis-section').classList.remove('hidden');
        
        // Start timer
        this.analysisStartTime = new Date();
        this.startTimer();
        
        // Disable check buttons
        const analyzeBtn = document.getElementById('analyze-btn');
        const analyzePrivateBtn = document.getElementById('analyze-private-btn');
        
        analyzeBtn.disabled = true;
        analyzeBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Checking...';
        
        if (analyzePrivateBtn) {
            analyzePrivateBtn.disabled = true;
            analyzePrivateBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Analyzing...';
        }
        
        // Emit start analysis event with env vars and optional GitHub token
        const analysisData = { 
            github_url: githubUrl,
            user_env_vars: this.userEnvVars
        };
        
        if (githubToken) {
            analysisData.github_token = githubToken;
        }
        
        this.socket.emit('start_analysis', analysisData);
        
        // Scroll to analysis section
        document.getElementById('analysis-section').scrollIntoView({ behavior: 'smooth' });
    }
    
    resetAnalysisState() {
        this.currentPhase = 0;
        this.questions = [];
        
        // Hide sections
        document.getElementById('questions-section').classList.add('hidden');
        document.getElementById('final-section').classList.add('hidden');
        document.getElementById('initial-results').classList.add('hidden');
        document.getElementById('env-vars-section').classList.add('hidden');
        
        // Reset phase cards
        document.querySelectorAll('.phase-card').forEach((card, index) => {
            card.classList.remove('active');
            const icon = card.querySelector('.phase-icon');
            const status = card.querySelector('.phase-status');
            
            icon.className = 'phase-icon w-8 h-8 rounded-full bg-gray-300 flex items-center justify-center';
            status.innerHTML = '<i class="fas fa-clock text-gray-400"></i>';
        });
        
        // Clear live updates
        document.getElementById('live-updates').innerHTML = '';
    }
    
    startTimer() {
        this.timerInterval = setInterval(() => {
            if (this.analysisStartTime) {
                const elapsed = Math.floor((new Date() - this.analysisStartTime) / 1000);
                const minutes = Math.floor(elapsed / 60);
                const seconds = elapsed % 60;
                document.getElementById('analysis-timer').textContent = 
                    `${minutes}:${seconds.toString().padStart(2, '0')}`;
            }
        }, 1000);
    }
    
    stopTimer() {
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
            this.timerInterval = null;
        }
    }
    
    handleAnalysisUpdate(data) {
        console.log('Analysis update:', data);
        
        // Add live update
        this.addLiveUpdate(data.status, data.message, data.timestamp);
        
        switch (data.status) {
            case 'started':
                this.updatePhase(1, 'running');
                break;
                
            case 'processing':
                // Keep current phase in processing state
                break;
                
            case 'phase_complete':
                this.handlePhaseComplete(data);
                break;
                
            case 'questions_ready':
                this.handleQuestionsReady(data);
                break;
                
            case 'completed':
                this.handleAnalysisComplete(data);
                break;
                
            case 'error':
                this.handleAnalysisError(data);
                break;
        }
    }
    
    handlePhaseComplete(data) {
        const phase = data.data.phase;
        
        if (phase === 'initial') {
            this.updatePhase(1, 'complete');
            this.showInitialResults(data.data.result);
            
            // Check if going to questions or final
            if (data.data.result.toLowerCase().includes('missing info needed:')) {
                this.updatePhase(2, 'running');
            } else {
                this.updatePhase(3, 'running');
            }
        } else if (phase === 'questions') {
            this.updatePhase(2, 'complete');
            // Questions will be handled by questions_ready event
        } else if (phase === 'final') {
            this.updatePhase(3, 'complete');
        }
    }
    
    handleQuestionsReady(data) {
        this.updatePhase(2, 'complete');
        this.showQuestions(data.data.questions);
    }
    
    handleAnalysisComplete(data) {
        this.updatePhase(3, 'complete');
        this.showFinalAssessment(data.data.final_assessment);
        this.stopTimer();
        
        // Re-enable check buttons
        const analyzeBtn = document.getElementById('analyze-btn');
        const analyzePrivateBtn = document.getElementById('analyze-private-btn');
        
        analyzeBtn.disabled = false;
        analyzeBtn.innerHTML = '<i class="fas fa-search mr-2"></i>Check';
        
        if (analyzePrivateBtn) {
            analyzePrivateBtn.disabled = false;
            analyzePrivateBtn.innerHTML = '<i class="fas fa-search mr-2"></i>Check';
        }
    }
    
    handleAnalysisError(data) {
        this.showError(data.message);
        this.stopTimer();
        
        // Re-enable check buttons
        const analyzeBtn = document.getElementById('analyze-btn');
        const analyzePrivateBtn = document.getElementById('analyze-private-btn');
        
        analyzeBtn.disabled = false;
        analyzeBtn.innerHTML = '<i class="fas fa-search mr-2"></i>Check';
        
        if (analyzePrivateBtn) {
            analyzePrivateBtn.disabled = false;
            analyzePrivateBtn.innerHTML = '<i class="fas fa-search mr-2"></i>Check';
        }
    }
    
    updatePhase(phaseNumber, status) {
        const phaseCard = document.getElementById(`phase-${phaseNumber}`);
        const icon = phaseCard.querySelector('.phase-icon');
        const statusIcon = phaseCard.querySelector('.phase-status');
        
        phaseCard.classList.add('active');
        
        switch (status) {
            case 'running':
                icon.className = 'phase-icon w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center text-white animate-pulse';
                statusIcon.innerHTML = '<i class="fas fa-spinner fa-spin text-blue-500"></i>';
                break;
                
            case 'complete':
                icon.className = 'phase-icon w-8 h-8 rounded-full bg-green-500 flex items-center justify-center text-white';
                statusIcon.innerHTML = '<i class="fas fa-check text-green-500"></i>';
                break;
                
            case 'error':
                icon.className = 'phase-icon w-8 h-8 rounded-full bg-red-500 flex items-center justify-center text-white';
                statusIcon.innerHTML = '<i class="fas fa-times text-red-500"></i>';
                break;
        }
    }
    
    addLiveUpdate(status, message, timestamp) {
        const updatesContainer = document.getElementById('live-updates');
        const updateElement = document.createElement('div');
        
        const statusClass = this.getStatusClass(status);
        const time = new Date(timestamp).toLocaleTimeString();
        
        updateElement.className = `p-3 rounded-lg ${statusClass} chat-bubble`;
        updateElement.innerHTML = `
            <div class="flex items-start space-x-3">
                <div class="flex-shrink-0">
                    ${this.getStatusIcon(status)}
                </div>
                <div class="flex-1">
                    <p class="text-sm font-medium">${message}</p>
                    <p class="text-xs opacity-75 mt-1">${time}</p>
                </div>
            </div>
        `;
        
        updatesContainer.appendChild(updateElement);
        updatesContainer.scrollTop = updatesContainer.scrollHeight;
    }
    
    getStatusClass(status) {
        switch (status) {
            case 'started':
            case 'processing':
                return 'status-running';
            case 'phase_complete':
            case 'completed':
            case 'questions_ready':
                return 'status-complete';
            case 'error':
                return 'status-error';
            default:
                return 'status-waiting';
        }
    }
    
    getStatusIcon(status) {
        switch (status) {
            case 'started':
                return '<i class="fas fa-play-circle text-blue-600"></i>';
            case 'processing':
                return '<i class="fas fa-cog fa-spin text-blue-600"></i>';
            case 'phase_complete':
            case 'completed':
                return '<i class="fas fa-check-circle text-green-600"></i>';
            case 'questions_ready':
                return '<i class="fas fa-question-circle text-orange-600"></i>';
            case 'error':
                return '<i class="fas fa-exclamation-circle text-red-600"></i>';
            default:
                return '<i class="fas fa-info-circle text-gray-600"></i>';
        }
    }
    
    showInitialResults(content) {
        document.getElementById('initial-content').innerHTML = this.formatMarkdown(content);
        document.getElementById('initial-results').classList.remove('hidden');
    }
    
    showQuestions(questionsText) {
        // Parse questions from the text
        const questions = this.parseQuestions(questionsText);
        this.questions = questions;
        
        const container = document.getElementById('questions-container');
        container.innerHTML = '';
        
        questions.forEach((question, index) => {
            const questionCard = document.createElement('div');
            questionCard.className = 'question-card bg-gray-50 p-6 rounded-lg border';
            
            questionCard.innerHTML = `
                <div class="mb-4">
                    <label class="block text-sm font-semibold text-gray-700 mb-2">
                        ${index + 1}. ${question.question}
                    </label>
                </div>
                <textarea 
                    id="question-${index}"
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    rows="3"
                    placeholder="Enter your answer here..."
                ></textarea>
            `;
            
            container.appendChild(questionCard);
        });
        
        document.getElementById('questions-section').classList.remove('hidden');
        document.getElementById('questions-section').scrollIntoView({ behavior: 'smooth' });
    }
    
    parseQuestions(questionsText) {
        // Parse numbered questions from the text
        const lines = questionsText.split('\n').filter(line => line.trim());
        const questions = [];
        
        lines.forEach((line, index) => {
            // Look for numbered questions
            if (line.match(/^\d+\./)) {
                questions.push({
                    id: index,
                    question: line.replace(/^\d+\.\s*/, '').trim(),
                    type: 'text'
                });
            }
        });
        
        // If no structured questions found, treat as single question block
        if (questions.length === 0 && questionsText.trim().length > 0) {
            questions.push({
                id: 1,
                question: questionsText.trim(),
                type: 'text'
            });
        }
        
        return questions;
    }
    
    submitResponses() {
        const responses = [];
        
        this.questions.forEach((question, index) => {
            const answer = document.getElementById(`question-${index}`).value.trim();
            if (answer) {
                responses.push({
                    question: question.question,
                    answer: answer
                });
            }
        });
        
        if (responses.length === 0) {
            this.showError('Please answer at least one question before submitting.');
            return;
        }
        
        // Update UI
        this.updatePhase(3, 'running');
        
        // Disable submit button
        const submitBtn = document.getElementById('submit-responses');
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Processing...';
        
        // Submit responses
        this.socket.emit('submit_responses', { responses: responses });
    }
    
    showFinalAssessment(content) {
        // Extract YES/NO answer
        const deployableMatch = content.match(/\*\*ANSWER:\s*(YES|NO)\*\*/i);
        const answerElement = document.getElementById('deployment-answer');
        
        if (deployableMatch) {
            const answer = deployableMatch[1].toUpperCase();
            answerElement.textContent = answer;
            
            if (answer === 'YES') {
                answerElement.className = 'text-8xl font-bold mb-4 deployable-yes';
            } else {
                answerElement.className = 'text-8xl font-bold mb-4 deployable-no';
            }
        } else {
            answerElement.textContent = '?';
            answerElement.className = 'text-8xl font-bold mb-4 text-gray-500';
        }
        
        document.getElementById('final-content').innerHTML = this.formatMarkdown(content);
        document.getElementById('final-section').classList.remove('hidden');
        document.getElementById('final-section').scrollIntoView({ behavior: 'smooth' });
        
        // Re-enable submit button
        const submitBtn = document.getElementById('submit-responses');
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="fas fa-paper-plane mr-2"></i>Submit Information';
    }
    
    formatMarkdown(text) {
        // Simple markdown-like formatting
        return text
            .replace(/## (.*)/g, '<h2 class="text-2xl font-bold mt-6 mb-4 text-gray-800">$1</h2>')
            .replace(/### (.*)/g, '<h3 class="text-xl font-semibold mt-4 mb-3 text-gray-700">$1</h3>')
            .replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold">$1</strong>')
            .replace(/\*(.*?)\*/g, '<em class="italic">$1</em>')
            .replace(/^- (.*)/gm, '<li class="ml-4 mb-1">$1</li>')
            .replace(/^\d+\. (.*)/gm, '<li class="ml-4 mb-1 list-decimal">$1</li>')
            .replace(/`([^`]+)`/g, '<code class="bg-gray-100 px-2 py-1 rounded text-sm font-mono">$1</code>')
            .replace(/\n\n/g, '</p><p class="mb-4">')
            .replace(/^/, '<p class="mb-4">')
            .replace(/$/, '</p>');
    }
    
    showError(message) {
        // Create error toast
        const toast = document.createElement('div');
        toast.className = 'fixed top-4 right-4 bg-red-500 text-white px-6 py-3 rounded-lg shadow-lg z-50 animate-pulse';
        toast.innerHTML = `
            <div class="flex items-center space-x-2">
                <i class="fas fa-exclamation-triangle"></i>
                <span>${message}</span>
            </div>
        `;
        
        document.body.appendChild(toast);
        
        // Remove after 5 seconds
        setTimeout(() => {
            toast.remove();
        }, 5000);
    }
    
    resetAnalysis() {
        // Reset all state
        this.resetAnalysisState();
        this.stopTimer();
        
        // Reset env vars
        this.userEnvVars = {};
        this.customEnvCounter = 0;
        
        // Clear all env var inputs
        this.clearAllEnvInputs();
        
        // Hide analysis section
        document.getElementById('analysis-section').classList.add('hidden');
        
        // Clear URL input
        document.getElementById('github-url').value = '';
        
        // Re-enable check buttons
        const analyzeBtn = document.getElementById('analyze-btn');
        const analyzePrivateBtn = document.getElementById('analyze-private-btn');
        
        analyzeBtn.disabled = false;
        analyzeBtn.innerHTML = '<i class="fas fa-search mr-2"></i>Check';
        
        if (analyzePrivateBtn) {
            analyzePrivateBtn.disabled = false;
            analyzePrivateBtn.innerHTML = '<i class="fas fa-search mr-2"></i>Check';
        }
        
        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new DeploymentAnalyzer();
}); 