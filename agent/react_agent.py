#!/usr/bin/env python3
"""
GitHub Repository Analyzer - ReAct Agent Implementation

This module implements a ReAct (Reasoning and Acting) agent using LangChain
for comprehensive GitHub repository analysis.
"""

import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from langchain.agents import create_react_agent, AgentExecutor
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import BaseTool
from langchain.prompts import PromptTemplate
from langchain.tools import Tool
from langchain.schema import AgentAction
import json
import re

from tools import (
    CloneRepositoryTool,
    GetRepositoryStructureTool,
    FlexibleReadFileTool,
    ListClonedRepositoriesTool,
    AnalyzeRepositoryTool,
    CleanupRepositoryTool
)


class GitHubRepoReActAgent:
    """
    A ReAct agent specialized for GitHub repository analysis.
    Uses LangChain's ReAct framework with custom repository tools.
    """
    
    def __init__(self, api_key: str, model_name: str = "anthropic/claude-3-5-sonnet-20241022", temperature: float = 0.1):
        """Initialize the ReAct agent."""
        self.api_key = api_key
        self.model_name = model_name
        self.temperature = temperature
        
        # Initialize LLM with OpenRouter configuration
        self.llm = ChatOpenAI(
            model=model_name,
            openai_api_key=api_key,
            openai_api_base="https://openrouter.ai/api/v1",
            temperature=temperature,
            max_tokens=4000
        )
        
        # Initialize tools
        self.tools = self._initialize_tools()
        
        # Create agent
        self.agent = self._create_agent()
        
        # Create agent executor with custom tool invocation
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            max_iterations=10,
            handle_parsing_errors=True
        )
    
    def _initialize_tools(self) -> List[BaseTool]:
        """Initialize all repository analysis tools."""
        return [
            CloneRepositoryTool(),
            GetRepositoryStructureTool(),
            FlexibleReadFileTool(),
            ListClonedRepositoriesTool(),
            AnalyzeRepositoryTool(),
            CleanupRepositoryTool()
        ]
    
    def _create_agent(self):
        """Create the ReAct agent with custom prompt."""
        
        # Create a prompt template compatible with create_react_agent
        prompt_template = """You are a GitHub Repository Analyzer assistant. Your goal is to help users analyze GitHub repositories comprehensively.

When using tools, follow these guidelines:
1. Always start by cloning the repository using clone_repository
2. Use get_repository_structure to understand the project layout
3. Read key files like README, package.json, requirements.txt, etc.
4. For read_file action, use this format: repo_full_name="owner/repo" file_path="filename"
5. Provide comprehensive analysis including architecture, dependencies, and recommendations

TOOLS:
------

You have access to the following tools:

{tools}

To use a tool, please use the following format:

```
Thought: Do I need to use a tool? Yes
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
```

When you have a response to say to the Human, or if you do not need to use a tool, you MUST use the format:

```
Thought: Do I need to use a tool? No
Final Answer: [your response here]
```

Begin!

Question: {input}
Thought: {agent_scratchpad}"""

        prompt = PromptTemplate.from_template(prompt_template)
        
        return create_react_agent(self.llm, self.tools, prompt)
    
    def analyze_repository(self, github_url: str, cleanup_after: bool = True) -> Dict[str, Any]:
        """
        Analyze a GitHub repository and provide comprehensive insights.
        
        Args:
            github_url: GitHub repository URL
            cleanup_after: Whether to cleanup the repository after analysis
            
        Returns:
            Dict containing analysis results
        """
        try:
            # Construct the input for the agent
            input_text = f"""
            Please analyze the GitHub repository: {github_url}
            
            I need a comprehensive analysis that includes:
            1. Repository architecture and overall structure
            2. Technology stack, frameworks, and dependencies used
            3. Key files and their purposes (README, config files, main code files)
            4. Detailed instructions on how to run/deploy the application
            5. Code organization and quality insights
            6. Any notable patterns, best practices, or areas for improvement
            
            Please clone the repository first, then explore its structure and files to provide detailed insights.
            {'After analysis, please clean up the cloned repository.' if cleanup_after else ''}
            """
            
            # Run the agent
            result = self.agent_executor.invoke({"input": input_text})
            
            return {
                "success": True,
                "repository_url": github_url,
                "analysis": result["output"],
                "model_used": self.model_name,
                "cleanup_performed": cleanup_after
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "repository_url": github_url
            }
    
    def ask_question(self, question: str) -> Dict[str, Any]:
        """
        Ask a general question to the agent about repositories or analysis.
        
        Args:
            question: The question to ask
            
        Returns:
            Dict containing the response
        """
        try:
            result = self.agent_executor.invoke({"input": question})
            
            return {
                "success": True,
                "question": question,
                "answer": result["output"],
                "model_used": self.model_name
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "question": question
            }
    
    def compare_repositories(self, repo_urls: List[str]) -> Dict[str, Any]:
        """
        Compare multiple repositories.
        
        Args:
            repo_urls: List of GitHub repository URLs to compare
            
        Returns:
            Dict containing comparison results
        """
        try:
            repos_text = "\n".join([f"- {url}" for url in repo_urls])
            input_text = f"""
            Please compare these GitHub repositories:
            {repos_text}
            
            For each repository, analyze:
            1. Technology stack and architecture
            2. Code organization and structure
            3. Dependencies and frameworks used
            4. How to run each application
            5. Strengths and weaknesses of each approach
            
            Then provide a detailed comparison highlighting:
            - Similarities and differences in architecture
            - Different approaches to solving similar problems
            - Code quality and organization differences
            - Performance and scalability considerations
            - Which repository might be better for different use cases
            
            Please clone each repository, analyze them thoroughly, and then provide the comparison.
            Clean up all repositories after analysis.
            """
            
            result = self.agent_executor.invoke({"input": input_text})
            
            return {
                "success": True,
                "repositories": repo_urls,
                "comparison": result["output"],
                "model_used": self.model_name
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "repositories": repo_urls
            }
    
    def get_deployment_guide(self, github_url: str) -> Dict[str, Any]:
        """
        Get detailed deployment instructions for a repository.
        
        Args:
            github_url: GitHub repository URL
            
        Returns:
            Dict containing deployment guide
        """
        try:
            input_text = f"""
            Please analyze the GitHub repository: {github_url}
            
            Focus specifically on creating a comprehensive deployment guide that includes:
            1. Prerequisites and system requirements
            2. Installation steps (dependencies, environment setup)
            3. Configuration requirements (environment variables, config files)
            4. Build process (if applicable)
            5. Running the application (development and production)
            6. Common deployment options (Docker, cloud platforms, etc.)
            7. Troubleshooting common issues
            8. Performance optimization tips
            
            Please examine all relevant files like README.md, package.json, requirements.txt, Dockerfile, 
            docker-compose.yml, Makefile, etc. to provide accurate and complete instructions.
            
            Clean up the repository after analysis.
            """
            
            result = self.agent_executor.invoke({"input": input_text})
            
            return {
                "success": True,
                "repository_url": github_url,
                "deployment_guide": result["output"],
                "model_used": self.model_name
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "repository_url": github_url
            }
    
    def cleanup_all_repositories(self) -> Dict[str, Any]:
        """Clean up all cloned repositories."""
        try:
            result = self.agent_executor.invoke({
                "input": "Please list all currently cloned repositories and then clean them all up."
            })
            
            return {
                "success": True,
                "cleanup_result": result["output"]
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            } 