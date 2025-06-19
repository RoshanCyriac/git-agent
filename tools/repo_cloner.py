import os
import tempfile
import shutil
import subprocess
from typing import Dict, Optional
from urllib.parse import urlparse

class RepositoryCloner:
    def __init__(self):
        self.temp_base_dir = tempfile.gettempdir()
        self.cloned_repos = {}  # Track cloned repositories
    
    def _validate_github_url(self, url: str) -> bool:
        """Validate if the provided URL is a valid GitHub repository URL."""
        try:
            parsed = urlparse(url)
            return parsed.netloc == "github.com" and len(parsed.path.split("/")) >= 3
        except:
            return False
    
    def _extract_repo_info(self, url: str) -> Dict[str, str]:
        """Extract owner and repository name from GitHub URL."""
        try:
            parsed = urlparse(url)
            parts = parsed.path.strip("/").split("/")
            return {
                "owner": parts[0],
                "repo": parts[1],
                "full_name": f"{parts[0]}/{parts[1]}"
            }
        except:
            return {}
    
    def _clean_unnecessary_files(self, repo_path: str) -> None:
        """Remove unnecessary files and folders from cloned repository."""
        unnecessary_items = [
            '.git',
            'node_modules',
            '__pycache__',
            '.pytest_cache',
            '.vscode',
            '.idea',
            '*.pyc',
            '*.pyo',
            '*.log',
            'dist',
            'build',
            '.DS_Store',
            'Thumbs.db'
        ]
        
        for item in unnecessary_items:
            item_path = os.path.join(repo_path, item)
            try:
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                elif os.path.isfile(item_path):
                    os.remove(item_path)
                # Handle glob patterns
                elif '*' in item:
                    import glob
                    for file_path in glob.glob(os.path.join(repo_path, '**', item), recursive=True):
                        if os.path.isfile(file_path):
                            os.remove(file_path)
            except Exception as e:
                # Silently continue if we can't remove some files
                pass
    
    def clone_repository(self, github_url: str, cleanup: bool = True) -> Dict:
        """
        Clone a GitHub repository to a temporary folder.
        
        Args:
            github_url: GitHub repository URL
            cleanup: Whether to remove unnecessary files after cloning
            
        Returns:
            Dict with success status, local path, and repository info
        """
        try:
            if not self._validate_github_url(github_url):
                return {"error": "Invalid GitHub URL provided"}
            
            repo_info = self._extract_repo_info(github_url)
            if not repo_info:
                return {"error": "Could not extract repository information from URL"}
            
            # Create a unique temporary directory for this repository
            temp_dir = tempfile.mkdtemp(prefix=f"repo_{repo_info['repo']}_")
            repo_path = os.path.join(temp_dir, repo_info['repo'])
            
            # Clone the repository
            try:
                result = subprocess.run(
                    ['git', 'clone', github_url, repo_path],
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout
                )
                
                if result.returncode != 0:
                    return {"error": f"Git clone failed: {result.stderr}"}
                
            except subprocess.TimeoutExpired:
                return {"error": "Repository clone timed out (5 minutes)"}
            except FileNotFoundError:
                return {"error": "Git is not installed or not found in PATH"}
            
            # Clean unnecessary files if requested
            if cleanup:
                self._clean_unnecessary_files(repo_path)
            
            # Store repository information
            self.cloned_repos[repo_info['full_name']] = {
                "path": repo_path,
                "temp_dir": temp_dir,
                "url": github_url,
                "cleaned": cleanup
            }
            
            return {
                "success": True,
                "repository": repo_info['full_name'],
                "local_path": repo_path,
                "temp_directory": temp_dir,
                "cleaned": cleanup,
                "owner": repo_info['owner'],
                "repo_name": repo_info['repo']
            }
            
        except Exception as e:
            return {"error": f"Clone operation failed: {str(e)}"}
    
    def get_cloned_repos(self) -> Dict:
        """Get list of currently cloned repositories."""
        return self.cloned_repos.copy()
    
    def cleanup_repo(self, repo_full_name: str) -> Dict:
        """
        Clean up a specific cloned repository.
        
        Args:
            repo_full_name: Repository name in format "owner/repo"
            
        Returns:
            Dict with cleanup status
        """
        try:
            if repo_full_name not in self.cloned_repos:
                return {"error": f"Repository {repo_full_name} not found in cloned repositories"}
            
            repo_data = self.cloned_repos[repo_full_name]
            temp_dir = repo_data['temp_dir']
            
            # Remove the temporary directory
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            
            # Remove from tracking
            del self.cloned_repos[repo_full_name]
            
            return {
                "success": True,
                "message": f"Successfully cleaned up {repo_full_name}",
                "removed_path": temp_dir
            }
            
        except Exception as e:
            return {"error": f"Cleanup failed: {str(e)}"}
    
    def cleanup_all(self) -> Dict:
        """Clean up all cloned repositories."""
        try:
            cleaned_repos = []
            errors = []
            
            for repo_name in list(self.cloned_repos.keys()):
                result = self.cleanup_repo(repo_name)
                if "success" in result:
                    cleaned_repos.append(repo_name)
                else:
                    errors.append(f"{repo_name}: {result.get('error', 'Unknown error')}")
            
            return {
                "success": True,
                "cleaned_repositories": cleaned_repos,
                "errors": errors,
                "total_cleaned": len(cleaned_repos)
            }
            
        except Exception as e:
            return {"error": f"Cleanup all failed: {str(e)}"}
    
    def get_repo_structure(self, repo_full_name: str, max_depth: int = 3) -> Dict:
        """
        Get the directory structure of a cloned repository.
        
        Args:
            repo_full_name: Repository name in format "owner/repo"
            max_depth: Maximum depth to traverse
            
        Returns:
            Dict with repository structure
        """
        try:
            if repo_full_name not in self.cloned_repos:
                return {"error": f"Repository {repo_full_name} not found in cloned repositories"}
            
            repo_path = self.cloned_repos[repo_full_name]['path']
            
            def get_structure(path, current_depth=0):
                items = {}
                if current_depth >= max_depth:
                    return items
                
                try:
                    for item in sorted(os.listdir(path)):
                        if item.startswith('.'):
                            continue
                        
                        item_path = os.path.join(path, item)
                        if os.path.isdir(item_path):
                            items[item] = {
                                "type": "directory",
                                "children": get_structure(item_path, current_depth + 1)
                            }
                        else:
                            items[item] = {
                                "type": "file",
                                "size": os.path.getsize(item_path)
                            }
                except PermissionError:
                    pass
                
                return items
            
            structure = get_structure(repo_path)
            
            return {
                "success": True,
                "repository": repo_full_name,
                "structure": structure,
                "max_depth": max_depth
            }
            
        except Exception as e:
            return {"error": f"Failed to get repository structure: {str(e)}"}
    
    def __del__(self):
        """Cleanup when the object is destroyed."""
        try:
            self.cleanup_all()
        except:
            pass
    
    def get_repository_structure(self, repo_full_name: str, max_depth: int = 3) -> Dict:
        """Alias for get_repo_structure for LangChain compatibility."""
        return self.get_repo_structure(repo_full_name, max_depth)
    
    def read_file(self, repo_full_name: str, file_path: str, max_chars: int = 10000) -> str:
        """
        Read contents of a specific file from a cloned repository.
        
        Args:
            repo_full_name: Repository name in format "owner/repo"
            file_path: Relative path to file within repository
            max_chars: Maximum characters to read
            
        Returns:
            File contents as string
        """
        if repo_full_name not in self.cloned_repos:
            raise Exception(f"Repository {repo_full_name} not found in cloned repositories")
        
        repo_path = self.cloned_repos[repo_full_name]['path']
        full_file_path = os.path.join(repo_path, file_path)
        
        if not os.path.exists(full_file_path):
            raise Exception(f"File {file_path} not found in repository {repo_full_name}")
        
        if not os.path.isfile(full_file_path):
            raise Exception(f"{file_path} is not a file")
        
        try:
            with open(full_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(max_chars)
            return content
        except Exception as e:
            raise Exception(f"Failed to read file {file_path}: {str(e)}")
    
    def analyze_repository(self, repo_full_name: str) -> Dict:
        """
        Analyze repository structure and contents.
        
        Args:
            repo_full_name: Repository name in format "owner/repo"
            
        Returns:
            Dict with analysis results
        """
        if repo_full_name not in self.cloned_repos:
            raise Exception(f"Repository {repo_full_name} not found in cloned repositories")
        
        repo_path = self.cloned_repos[repo_full_name]['path']
        
        analysis = {
            "total_files": 0,
            "total_directories": 0,
            "file_extensions": {},
            "key_files": [],
            "readme_content": "",
            "technology_indicators": [],
            "size_bytes": 0
        }
        
        # Common important files to look for
        important_files = [
            'README.md', 'README.txt', 'README.rst', 'README',
            'package.json', 'package-lock.json', 'yarn.lock',
            'requirements.txt', 'setup.py', 'pyproject.toml', 'Pipfile',
            'Dockerfile', 'docker-compose.yml', 'docker-compose.yaml',
            'Makefile', 'CMakeLists.txt', 'build.gradle', 'pom.xml',
            'Cargo.toml', 'go.mod', 'composer.json',
            '.gitignore', '.env', '.env.example',
            'LICENSE', 'LICENSE.txt', 'MIT-LICENSE', 'COPYING'
        ]
        
        # Technology indicators
        tech_indicators = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.jsx': 'React',
            '.tsx': 'React TypeScript',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.cs': 'C#',
            '.php': 'PHP',
            '.rb': 'Ruby',
            '.go': 'Go',
            '.rs': 'Rust',
            '.swift': 'Swift',
            '.kt': 'Kotlin',
            '.scala': 'Scala',
            '.html': 'HTML',
            '.css': 'CSS',
            '.scss': 'SASS',
            '.less': 'LESS',
            '.vue': 'Vue.js',
            '.r': 'R',
            '.m': 'MATLAB/Objective-C',
            '.sql': 'SQL'
        }
        
        try:
            # Walk through directory structure
            for root, dirs, files in os.walk(repo_path):
                analysis["total_directories"] += len(dirs)
                analysis["total_files"] += len(files)
                
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    # Add file size
                    try:
                        analysis["size_bytes"] += os.path.getsize(file_path)
                    except:
                        pass
                    
                    # Track file extensions
                    ext = os.path.splitext(file)[1].lower()
                    if ext:
                        analysis["file_extensions"][ext] = analysis["file_extensions"].get(ext, 0) + 1
                        
                        # Track technology indicators
                        if ext in tech_indicators:
                            tech = tech_indicators[ext]
                            if tech not in analysis["technology_indicators"]:
                                analysis["technology_indicators"].append(tech)
                    
                    # Check for important files
                    if file in important_files:
                        analysis["key_files"].append(os.path.relpath(file_path, repo_path))
            
            # Try to read README content
            for readme_file in ['README.md', 'README.txt', 'README.rst', 'README']:
                readme_path = os.path.join(repo_path, readme_file)
                if os.path.exists(readme_path):
                    try:
                        with open(readme_path, 'r', encoding='utf-8', errors='ignore') as f:
                            analysis["readme_content"] = f.read()[:2000]  # First 2000 chars
                        break
                    except:
                        continue
            
            # Sort file extensions by count
            analysis["file_extensions"] = dict(
                sorted(analysis["file_extensions"].items(), key=lambda x: x[1], reverse=True)
            )
            
        except Exception as e:
            analysis["error"] = str(e)
        
        return analysis
    
    def list_cloned_repositories(self):
        """
        List all cloned repositories with their metadata.
        
        Returns:
            List of dictionaries with repository information
        """
        repos = []
        for repo_name, repo_data in self.cloned_repos.items():
            repos.append({
                "name": repo_name,
                "path": repo_data["path"],
                "url": repo_data["url"],
                "cleaned": repo_data["cleaned"],
                "temp_dir": repo_data["temp_dir"]
            })
        return repos
    
    def cleanup_repository(self, repo_full_name: str) -> Dict:
        """Alias for cleanup_repo for LangChain compatibility."""
        return self.cleanup_repo(repo_full_name) 