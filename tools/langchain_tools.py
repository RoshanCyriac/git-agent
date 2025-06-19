"""
LangChain-compatible tools for the GitHub Repository Analyzer.
These tools convert the functionality of RepositoryCloner into individual BaseTool implementations.
"""

import json
import os
from typing import Dict, Any, List, Optional, Type
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from .repo_cloner import RepositoryCloner

# Shared RepositoryCloner instance
_shared_repo_cloner = None

def get_shared_repo_cloner():
    """Get or create the shared RepositoryCloner instance."""
    global _shared_repo_cloner
    if _shared_repo_cloner is None:
        _shared_repo_cloner = RepositoryCloner()
    return _shared_repo_cloner


class CloneRepositoryInput(BaseModel):
    """Input for cloning a repository."""
    github_url: str = Field(description="GitHub repository URL to clone")
    cleanup: bool = Field(default=True, description="Whether to cleanup after analysis")


class CloneRepositoryTool(BaseTool):
    """Tool for cloning GitHub repositories."""
    name: str = "clone_repository"
    description: str = """Clone a GitHub repository to analyze its structure and contents.
    Input should be a GitHub URL. Returns repository information and local path."""
    args_schema: Type[BaseModel] = CloneRepositoryInput
    
    def _run(self, github_url: str, cleanup: bool = True) -> str:
        """Clone repository synchronously."""
        try:
            repo_cloner = get_shared_repo_cloner()
            result = repo_cloner.clone_repository(github_url, cleanup=cleanup)
            
            if "error" in result:
                return json.dumps({
                    "success": False,
                    "error": result["error"],
                    "repository_url": github_url
                })
            
            return json.dumps({
                "success": True,
                "repository_url": github_url,
                "local_path": result.get("local_path"),
                "repo_full_name": result.get("repository"),
                "owner": result.get("owner"),
                "repo_name": result.get("repo_name"),
                "message": "Repository cloned successfully"
            })
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e),
                "repository_url": github_url
            })
    
    async def _arun(self, github_url: str, cleanup: bool = True) -> str:
        """Clone repository asynchronously."""
        return self._run(github_url, cleanup)


class GetRepositoryStructureInput(BaseModel):
    """Input for getting repository structure."""
    repo_full_name: str = Field(description="Full repository name (e.g., 'user/repo')")
    max_depth: int = Field(default=3, description="Maximum depth to traverse")


class GetRepositoryStructureTool(BaseTool):
    """Tool for getting the structure of a cloned repository."""
    name: str = "get_repository_structure"
    description: str = """Get the directory structure of a cloned repository.
    Input should be the repository full name. Returns JSON tree structure."""
    args_schema: Type[BaseModel] = GetRepositoryStructureInput
    
    def _run(self, repo_full_name: str, max_depth: int = 3) -> str:
        """Get repository structure synchronously."""
        try:
            repo_cloner = get_shared_repo_cloner()
            result = repo_cloner.get_repository_structure(repo_full_name, max_depth)
            
            if "error" in result:
                return json.dumps({
                    "success": False,
                    "error": result["error"],
                    "repo_full_name": repo_full_name
                })
            
            return json.dumps({
                "success": True,
                "repo_full_name": repo_full_name,
                "structure": result.get("structure")
            })
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e),
                "repo_full_name": repo_full_name
            })
    
    async def _arun(self, repo_full_name: str, max_depth: int = 3) -> str:
        """Get repository structure asynchronously."""
        return self._run(repo_full_name, max_depth)


class ReadFileInput(BaseModel):
    """Input for reading a file from repository."""
    repo_full_name: str = Field(description="Full repository name (e.g., 'user/repo')")
    file_path: str = Field(description="Path to file within repository")
    max_chars: int = Field(default=10000, description="Maximum characters to read")

    @classmethod
    def parse_from_string(cls, input_str: str):
        """Parse input from string that might be JSON."""
        try:
            import json as json_lib
            if isinstance(input_str, str) and input_str.strip().startswith('{'):
                parsed = json_lib.loads(input_str)
                return cls(**parsed)
        except:
            pass
        return None


class FlexibleReadFileTool(BaseTool):
    """Tool for reading files with flexible input parsing."""
    name: str = "read_file"
    description: str = """Read a specific file from a cloned repository.
    Input: repo_full_name and file_path
    Example: repo_full_name="owner/repo" file_path="README.md"
    Or: {"repo_full_name": "owner/repo", "file_path": "README.md"}"""
    
    def _run(self, tool_input: str = None, **kwargs) -> str:
        """Read file with flexible input parsing."""
        try:
            # Handle different input formats
            repo_full_name = None
            file_path = None
            max_chars = 10000
            
            # Method 1: Direct parameters in kwargs
            if 'repo_full_name' in kwargs and 'file_path' in kwargs:
                repo_full_name = kwargs['repo_full_name']
                file_path = kwargs['file_path']
                max_chars = kwargs.get('max_chars', 10000)
            
            # Method 2: tool_input as string (from LangChain)
            elif tool_input:
                # Try to parse as key=value format
                if '=' in tool_input:
                    parts = tool_input.split()
                    params = {}
                    for part in parts:
                        if '=' in part:
                            key, value = part.split('=', 1)
                            # Remove quotes if present
                            value = value.strip('"\'')
                            params[key] = value
                    
                    repo_full_name = params.get('repo_full_name')
                    file_path = params.get('file_path')
                    max_chars = int(params.get('max_chars', 10000))
                
                # Try to parse as JSON
                elif tool_input.strip().startswith('{'):
                    try:
                        parsed = json.loads(tool_input)
                        repo_full_name = parsed.get('repo_full_name')
                        file_path = parsed.get('file_path')
                        max_chars = parsed.get('max_chars', 10000)
                    except json.JSONDecodeError:
                        pass
            
            # Method 3: Check if repo_full_name contains JSON string
            elif 'repo_full_name' in kwargs and isinstance(kwargs['repo_full_name'], str):
                input_str = kwargs['repo_full_name']
                if input_str.strip().startswith('{'):
                    try:
                        parsed = json.loads(input_str)
                        repo_full_name = parsed.get('repo_full_name')
                        file_path = parsed.get('file_path')
                        max_chars = parsed.get('max_chars', 10000)
                    except json.JSONDecodeError:
                        pass
                
                # If not JSON, treat as normal repo name
                if not file_path:
                    repo_full_name = input_str
                    file_path = kwargs.get('file_path', '')
            
            if not repo_full_name or not file_path:
                return json.dumps({
                    "success": False,
                    "error": f"Missing required parameters. Got tool_input: {tool_input}, kwargs: {kwargs}",
                    "expected": "repo_full_name and file_path"
                })
            
            repo_cloner = get_shared_repo_cloner()
            content = repo_cloner.read_file(repo_full_name, file_path, max_chars)
            return json.dumps({
                "success": True,
                "repo_full_name": repo_full_name,
                "file_path": file_path,
                "content": content,
                "chars_read": len(content)
            })
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e),
                "input_received": f"tool_input: {tool_input}, kwargs: {kwargs}"
            })
    
    async def _arun(self, tool_input: str = None, **kwargs) -> str:
        """Read file asynchronously."""
        return self._run(tool_input, **kwargs)


class ListClonedRepositoriesInput(BaseModel):
    """Input for listing cloned repositories."""
    pass


class ListClonedRepositoriesTool(BaseTool):
    """Tool for listing all cloned repositories."""
    name: str = "list_cloned_repositories"
    description: str = """List all currently cloned repositories.
    No input required. Returns list of cloned repositories with metadata."""
    args_schema: Type[BaseModel] = ListClonedRepositoriesInput
    
    def _run(self) -> str:
        """List repositories synchronously."""
        try:
            repo_cloner = get_shared_repo_cloner()
            repos = repo_cloner.list_cloned_repositories()
            return json.dumps({
                "success": True,
                "repositories": repos,
                "count": len(repos)
            })
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e)
            })
    
    async def _arun(self) -> str:
        """List repositories asynchronously."""
        return self._run()


class AnalyzeRepositoryInput(BaseModel):
    """Input for analyzing repository."""
    repo_full_name: str = Field(description="Full repository name (e.g., 'user/repo')")


class AnalyzeRepositoryTool(BaseTool):
    """Tool for analyzing repository contents and structure."""
    name: str = "analyze_repository"
    description: str = """Analyze the contents and structure of a cloned repository.
    Input should be repository full name. Returns detailed analysis."""
    args_schema: Type[BaseModel] = AnalyzeRepositoryInput
    
    def _run(self, repo_full_name: str) -> str:
        """Analyze repository synchronously."""
        try:
            repo_cloner = get_shared_repo_cloner()
            analysis = repo_cloner.analyze_repository(repo_full_name)
            return json.dumps({
                "success": True,
                "repo_full_name": repo_full_name,
                "analysis": analysis
            })
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e),
                "repo_full_name": repo_full_name
            })
    
    async def _arun(self, repo_full_name: str) -> str:
        """Analyze repository asynchronously."""
        return self._run(repo_full_name)


class CleanupRepositoryInput(BaseModel):
    """Input for cleaning up repository."""
    repo_full_name: str = Field(description="Full repository name (e.g., 'user/repo')")


class CleanupRepositoryTool(BaseTool):
    """Tool for cleaning up cloned repositories."""
    name: str = "cleanup_repository"
    description: str = """Clean up a specific cloned repository to free disk space.
    Input should be repository full name. Returns cleanup confirmation."""
    args_schema: Type[BaseModel] = CleanupRepositoryInput
    
    def _run(self, repo_full_name: str) -> str:
        """Cleanup repository synchronously."""
        try:
            repo_cloner = get_shared_repo_cloner()
            result = repo_cloner.cleanup_repository(repo_full_name)
            return json.dumps({
                "success": True,
                "repo_full_name": repo_full_name,
                "message": f"Repository {repo_full_name} cleaned up successfully",
                "freed_space": result.get("freed_space", "Unknown")
            })
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e),
                "repo_full_name": repo_full_name
            })
    
    async def _arun(self, repo_full_name: str) -> str:
        """Cleanup repository asynchronously."""
        return self._run(repo_full_name) 