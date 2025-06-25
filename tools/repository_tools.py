"""
Repository Analysis Tools for LangChain

This module provides LangChain-compatible tools that wrap the repository
analysis functionality from the main application.
"""

import os
import sys
import tempfile
import shutil
import subprocess
import random
import string
from typing import Dict, Any, Optional
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

# Add parent directory to path to import from app.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Global dictionary to store cloned repositories
_cloned_repositories = {}


class CloneRepositoryInput(BaseModel):
    """Input for CloneRepositoryTool."""
    github_url: str = Field(description="GitHub repository URL to clone")
    github_token: Optional[str] = Field(default=None, description="GitHub token for private repositories")


class CloneRepositoryTool(BaseTool):
    """Tool for cloning GitHub repositories."""
    
    name = "clone_repository"
    description = "Clone a GitHub repository to local filesystem for analysis"
    args_schema = CloneRepositoryInput
    
    def _run(self, github_url: str, github_token: Optional[str] = None) -> str:
        """Clone a GitHub repository."""
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
                # Store the cloned repository info
                repo_key = github_url.split('/')[-2] + '/' + github_url.split('/')[-1].replace('.git', '')
                _cloned_repositories[repo_key] = local_path
                return f"Successfully cloned repository to {local_path}. Repository key: {repo_key}"
            else:
                return f"Failed to clone repository: {result.stderr}"
                
        except subprocess.TimeoutExpired:
            return "Repository cloning timed out"
        except Exception as e:
            return f"Error cloning repository: {str(e)}"


class GetRepositoryStructureInput(BaseModel):
    """Input for GetRepositoryStructureTool."""
    repo_full_name: str = Field(description="Full repository name (owner/repo)")


class GetRepositoryStructureTool(BaseTool):
    """Tool for getting repository structure."""
    
    name = "get_repository_structure"
    description = "Get the directory structure of a cloned repository"
    args_schema = GetRepositoryStructureInput
    
    def _run(self, repo_full_name: str) -> str:
        """Get the structure of the repository."""
        try:
            if repo_full_name not in _cloned_repositories:
                return f"Repository {repo_full_name} not found. Please clone it first."
            
            local_path = _cloned_repositories[repo_full_name]
            
            if not os.path.exists(local_path):
                return f"Repository path {local_path} does not exist."
            
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
            return f"Error getting repository structure: {str(e)}"


class FlexibleReadFileInput(BaseModel):
    """Input for FlexibleReadFileTool."""
    repo_full_name: str = Field(description="Full repository name (owner/repo)")
    file_path: str = Field(description="Path to the file within the repository")


class FlexibleReadFileTool(BaseTool):
    """Tool for reading files from cloned repositories."""
    
    name = "read_file"
    description = "Read the contents of a file from a cloned repository"
    args_schema = FlexibleReadFileInput
    
    def _run(self, repo_full_name: str, file_path: str) -> str:
        """Read a file from the repository."""
        try:
            if repo_full_name not in _cloned_repositories:
                return f"Repository {repo_full_name} not found. Please clone it first."
            
            local_path = _cloned_repositories[repo_full_name]
            full_file_path = os.path.join(local_path, file_path)
            
            if not os.path.exists(full_file_path):
                return f"File {file_path} does not exist in repository {repo_full_name}"
            
            if os.path.isdir(full_file_path):
                return f"{file_path} is a directory, not a file"
            
            try:
                with open(full_file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Limit content size for large files
                    if len(content) > 10000:
                        content = content[:10000] + "\n\n... (file truncated due to size)"
                    return f"Contents of {file_path}:\n\n{content}"
            except UnicodeDecodeError:
                return f"File {file_path} appears to be a binary file and cannot be read as text"
            
        except Exception as e:
            return f"Error reading file {file_path}: {str(e)}"


class ListClonedRepositoriesTool(BaseTool):
    """Tool for listing cloned repositories."""
    
    name = "list_cloned_repositories"
    description = "List all currently cloned repositories"
    
    def _run(self) -> str:
        """List all cloned repositories."""
        if not _cloned_repositories:
            return "No repositories are currently cloned."
        
        repo_list = []
        for repo_name, local_path in _cloned_repositories.items():
            if os.path.exists(local_path):
                repo_list.append(f"- {repo_name}: {local_path}")
            else:
                repo_list.append(f"- {repo_name}: {local_path} (path no longer exists)")
        
        return "Currently cloned repositories:\n" + "\n".join(repo_list)


class AnalyzeRepositoryInput(BaseModel):
    """Input for AnalyzeRepositoryTool."""
    repo_full_name: str = Field(description="Full repository name (owner/repo)")


class AnalyzeRepositoryTool(BaseTool):
    """Tool for analyzing repository content."""
    
    name = "analyze_repository"
    description = "Analyze key files and content from a cloned repository"
    args_schema = AnalyzeRepositoryInput
    
    def _run(self, repo_full_name: str) -> str:
        """Analyze key content from the repository."""
        try:
            if repo_full_name not in _cloned_repositories:
                return f"Repository {repo_full_name} not found. Please clone it first."
            
            local_path = _cloned_repositories[repo_full_name]
            
            if not os.path.exists(local_path):
                return f"Repository path {local_path} does not exist."
            
            content_summary = []
            
            # Key files to analyze
            key_files = [
                'package.json', 'requirements.txt', 'Dockerfile', 'docker-compose.yml',
                'app.py', 'main.py', 'index.js', 'server.js', 'app.js',
                'README.md', '.env.example', 'config.py', 'settings.py',
                'pom.xml', 'build.gradle', 'Cargo.toml', 'go.mod'
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
            
            if not content_summary:
                return f"No key files found in repository {repo_full_name}"
            
            return f"Key files analysis for {repo_full_name}:" + '\n'.join(content_summary)
        except Exception as e:
            return f"Error analyzing repository: {str(e)}"


class CleanupRepositoryInput(BaseModel):
    """Input for CleanupRepositoryTool."""
    repo_full_name: Optional[str] = Field(default=None, description="Full repository name (owner/repo). If not provided, cleans up all repositories.")


class CleanupRepositoryTool(BaseTool):
    """Tool for cleaning up cloned repositories."""
    
    name = "cleanup_repository"
    description = "Clean up cloned repositories from local filesystem"
    args_schema = CleanupRepositoryInput
    
    def _run(self, repo_full_name: Optional[str] = None) -> str:
        """Clean up cloned repositories."""
        try:
            if repo_full_name:
                # Clean up specific repository
                if repo_full_name not in _cloned_repositories:
                    return f"Repository {repo_full_name} not found in cloned repositories."
                
                local_path = _cloned_repositories[repo_full_name]
                if os.path.exists(local_path):
                    shutil.rmtree(local_path)
                    del _cloned_repositories[repo_full_name]
                    return f"Successfully cleaned up repository {repo_full_name} at {local_path}"
                else:
                    del _cloned_repositories[repo_full_name]
                    return f"Repository {repo_full_name} path no longer exists, removed from tracking."
            else:
                # Clean up all repositories
                cleaned_repos = []
                for repo_name, local_path in list(_cloned_repositories.items()):
                    if os.path.exists(local_path):
                        shutil.rmtree(local_path)
                        cleaned_repos.append(f"{repo_name} at {local_path}")
                    del _cloned_repositories[repo_name]
                
                if cleaned_repos:
                    return f"Successfully cleaned up {len(cleaned_repos)} repositories:\n" + "\n".join(f"- {repo}" for repo in cleaned_repos)
                else:
                    return "No repositories to clean up."
                    
        except Exception as e:
            return f"Error cleaning up repository: {str(e)}" 