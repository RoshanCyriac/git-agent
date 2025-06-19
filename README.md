# GitHub Repository Analyzer - ReAct Agent

A powerful AI agent that uses LangChain's ReAct (Reasoning and Acting) framework to intelligently analyze GitHub repositories. The agent can clone repositories, explore their structure, read files, and provide comprehensive architectural analysis with deployment instructions.

## 🚀 Features

### 🤖 ReAct Agent Capabilities
- **Intelligent Tool Usage**: Agent decides which tools to use based on the task
- **Multi-step Reasoning**: Follows a thought-action-observation loop for comprehensive analysis
- **Self-directed Exploration**: Autonomously explores repository structure and files
- **Contextual Analysis**: Builds understanding progressively through tool interactions

### 🛠️ Specialized Tools
- **Repository Cloner**: Downloads and cleans GitHub repositories
- **Structure Analyzer**: Maps directory hierarchies and file organization
- **File Reader**: Reads and analyzes specific files (README, config, source code)
- **Technology Detector**: Identifies programming languages, frameworks, and dependencies
- **Architecture Analyzer**: Provides detailed technical insights

### 📊 Analysis Capabilities
- **Comprehensive Repository Analysis**: Complete architectural overview
- **Repository Comparison**: Side-by-side analysis of multiple projects
- **Deployment Guide Generation**: Step-by-step deployment instructions
- **Technology Stack Analysis**: Detailed breakdown of technologies used
- **Code Quality Assessment**: Organization and best practices evaluation

## 🏗️ Architecture

```
GitHub Repository Analyzer - ReAct Agent
├── 🤖 ReAct Agent (agent/react_agent.py)
│   ├── LangChain ReAct Framework
│   ├── Custom Prompt Template
│   └── Agent Executor with Tools
├── 🛠️ LangChain Tools (tools/langchain_tools.py)
│   ├── CloneRepositoryTool
│   ├── GetRepositoryStructureTool
│   ├── ReadFileTool
│   ├── AnalyzeRepositoryTool
│   ├── ListClonedRepositoriesTool
│   └── CleanupRepositoryTool
├── 🔧 Repository Cloner (tools/repo_cloner.py)
│   └── Core cloning and file management
└── 🖥️ Interactive Interface (main_react.py)
    └── User-friendly menu system
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Git installed and accessible in PATH
- OpenRouter API key

### Installation

1. **Clone and setup**:
   ```bash
   git clone <your-repo-url>
   cd repo-analyzer
   python3 -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenRouter API key
   ```

3. **Run the ReAct Agent**:
   ```bash
   python main_react.py
   ```

## 🎯 Usage Examples

### 1. Comprehensive Repository Analysis
```python
from agent.react_agent import GitHubRepoReActAgent

agent = GitHubRepoReActAgent(api_key="your-api-key")

# Analyze a repository
result = agent.analyze_repository(
    "https://github.com/user/repo",
    cleanup_after=True
)

print(result['analysis'])
```

### 2. Repository Comparison
```python
# Compare multiple repositories
result = agent.compare_repositories([
    "https://github.com/user/repo1",
    "https://github.com/user/repo2"
])

print(result['comparison'])
```

### 3. Deployment Guide Generation
```python
# Get detailed deployment instructions
result = agent.get_deployment_guide("https://github.com/user/repo")
print(result['deployment_guide'])
```

### 4. Interactive Questions
```python
# Ask specific questions about repositories
result = agent.ask_question(
    "How do I set up the development environment for this React project?"
)
print(result['answer'])
```

## 🔧 ReAct Agent Workflow

The agent follows the ReAct pattern:

```
Question: Analyze repository X
Thought: I need to clone the repository first to examine its structure
Action: clone_repository
Action Input: {"github_url": "https://github.com/user/repo"}
Observation: Successfully cloned repo to /tmp/repo_xyz

Thought: Now I should examine the overall structure
Action: get_repository_structure  
Action Input: {"repo_full_name": "user/repo", "max_depth": 3}
Observation: Repository has src/, tests/, package.json, README.md...

Thought: I should read the README to understand the project
Action: read_file
Action Input: {"repo_full_name": "user/repo", "file_path": "README.md"}
Observation: This is a React application that...

... (continues until comprehensive analysis is complete)

Final Answer: [Detailed architectural analysis with deployment instructions]
```

## 🛠️ Custom Tools

### CloneRepositoryTool
- **Purpose**: Downloads GitHub repositories to temporary directories
- **Features**: URL validation, automatic cleanup, error handling
- **Output**: Repository metadata and local path information

### GetRepositoryStructureTool  
- **Purpose**: Maps directory structure and file organization
- **Features**: Configurable depth, excludes unnecessary files
- **Output**: JSON tree structure of the repository

### ReadFileTool
- **Purpose**: Reads specific files from cloned repositories
- **Features**: Encoding handling, size limits, error recovery
- **Output**: File contents with metadata

### AnalyzeRepositoryTool
- **Purpose**: Performs deep technical analysis
- **Features**: Technology detection, dependency analysis, file counting
- **Output**: Comprehensive technical breakdown

### ListClonedRepositoriesTool
- **Purpose**: Manages cloned repository inventory
- **Features**: Lists active repositories with metadata
- **Output**: Current repository status and paths

### CleanupRepositoryTool
- **Purpose**: Removes cloned repositories from local storage
- **Features**: Selective or bulk cleanup, path validation
- **Output**: Cleanup confirmation and freed space

## 📋 Analysis Output Structure

### Repository Analysis
```json
{
  "success": true,
  "repository_url": "https://github.com/user/repo",
  "analysis": "Comprehensive analysis text...",
  "model_used": "anthropic/claude-3-5-sonnet-20241022",
  "cleanup_performed": true
}
```

### Repository Comparison
```json
{
  "success": true,
  "repositories": ["repo1", "repo2"],
  "comparison": "Detailed comparison analysis...",
  "model_used": "anthropic/claude-3-5-sonnet-20241022"
}
```

### Deployment Guide
```json
{
  "success": true,
  "repository_url": "https://github.com/user/repo",
  "deployment_guide": "Step-by-step deployment instructions...",
  "model_used": "anthropic/claude-3-5-sonnet-20241022"
}
```

## ⚙️ Configuration

### Environment Variables
```bash
OPENROUTER_API_KEY=your_api_key_here
OPENROUTER_MODEL=anthropic/claude-3-5-sonnet-20241022
```

### Agent Configuration
```python
agent = GitHubRepoReActAgent(
    api_key="your-api-key",
    model_name="anthropic/claude-3-5-sonnet-20241022"  # Optional
)

# Agent executor settings
agent.agent_executor.max_iterations = 15  # Max reasoning steps
agent.agent_executor.verbose = True       # Show reasoning process
```

## 🔍 Supported Models

The agent works with any OpenRouter-compatible model:
- `anthropic/claude-3-5-sonnet-20241022` (recommended)
- `openai/gpt-4`
- `openai/gpt-3.5-turbo`
- `mistralai/mistral-7b-instruct`
- And many more...

## 🎯 Use Cases

### Software Development
- **Architecture Review**: Analyze existing codebases for improvements
- **Technology Assessment**: Evaluate different approaches to similar problems
- **Onboarding**: Generate comprehensive setup guides for new team members

### DevOps & Deployment
- **Deployment Automation**: Create standardized deployment procedures
- **Environment Setup**: Generate development environment instructions
- **Configuration Management**: Analyze and document configuration requirements

### Code Analysis
- **Quality Assessment**: Evaluate code organization and best practices
- **Dependency Analysis**: Understand project dependencies and requirements
- **Security Review**: Identify potential security considerations

### Research & Learning
- **Technology Exploration**: Learn about new frameworks and patterns
- **Comparative Analysis**: Understand different approaches to similar problems
- **Best Practices**: Identify industry standards and recommended practices

## 🔧 Advanced Usage

### Custom Tool Integration
```python
from langchain_core.tools import BaseTool

class CustomAnalysisTool(BaseTool):
    name = "custom_analysis"
    description = "Performs custom analysis..."
    
    def _run(self, input_data: str) -> str:
        # Custom analysis logic
        return "Analysis result"

# Add to agent
agent.tools.append(CustomAnalysisTool())
```

### Prompt Customization
```python
# Modify the agent's reasoning template
custom_template = """
You are a specialized repository analyst...
[Custom instructions]
"""

agent._create_agent_with_custom_prompt(custom_template)
```

## 🚨 Error Handling

The agent includes comprehensive error handling:
- **Network Issues**: Automatic retry logic for API calls
- **Repository Access**: Graceful handling of private/non-existent repos
- **File System**: Safe temporary file management
- **Tool Failures**: Fallback strategies for tool execution errors

## 🔒 Security Considerations

- **Temporary Files**: All cloned repositories are stored in temporary directories
- **Automatic Cleanup**: Repositories are automatically cleaned up after analysis
- **API Key Protection**: Environment variable-based API key management
- **Input Validation**: URL and input parameter validation

## 📈 Performance

### Optimization Features
- **Selective File Reading**: Only reads necessary files to reduce processing time
- **Parallel Processing**: Tools can be executed concurrently where possible
- **Caching**: Repository structure caching to avoid redundant operations
- **Memory Management**: Automatic cleanup of large repositories

### Typical Performance
- **Simple Analysis**: 30-60 seconds
- **Complex Analysis**: 2-5 minutes
- **Repository Comparison**: 3-10 minutes (depending on repository size)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add your custom tools or improvements
4. Test with various repository types
5. Submit a pull request

## 📄 License

This project is open source. Please check the license file for details.

## 🆘 Support

For issues and questions:
1. Check the error messages and agent reasoning output
2. Verify all requirements are installed correctly
3. Ensure your OpenRouter API key is valid
4. Check that Git is installed and accessible

## 🎉 Example Output

When analyzing a repository, the ReAct agent provides output like:

```
🤖 REACT AGENT ANALYSIS RESULTS
================================================================================
📁 Repository: https://github.com/facebook/react
🧠 Model Used: anthropic/claude-3-5-sonnet-20241022
🧹 Cleanup Performed: Yes

🔍 AI Analysis:
================================================================================

# React Repository Architecture Analysis

## Repository Overview
React is a JavaScript library for building user interfaces, maintained by Facebook and the community. This repository contains the core React library source code, along with extensive documentation, examples, and development tools.

## Architecture & Structure

### Core Architecture
- **Modular Design**: The codebase is organized into distinct packages under the `packages/` directory
- **Monorepo Structure**: Uses a monorepo approach with multiple related packages
- **Build System**: Sophisticated build system using Rollup and custom scripts

### Key Directories
- `packages/react/`: Core React library
- `packages/react-dom/`: DOM-specific React functionality  
- `packages/scheduler/`: Task scheduling utilities
- `scripts/`: Build and development scripts
- `fixtures/`: Test applications and examples

## Technology Stack

### Primary Technologies
- **JavaScript (ES6+)**: Core implementation language
- **Flow**: Static type checking (being migrated to TypeScript)
- **Jest**: Testing framework
- **Rollup**: Module bundler for production builds
- **Prettier**: Code formatting
- **ESLint**: Code linting

### Development Tools
- **Yarn**: Package management
- **Babel**: JavaScript compilation
- **Node.js**: Development environment
- **CircleCI**: Continuous integration

## How to Run/Deploy

### Development Setup
1. **Prerequisites**: Node.js 14+, Yarn 1.x
2. **Clone and Install**:
   ```bash
   git clone https://github.com/facebook/react.git
   cd react
   yarn install
   ```

3. **Build React**:
   ```bash
   yarn build
   ```

4. **Run Tests**:
   ```bash
   yarn test
   ```

### Development Workflow
- **Local Development**: `yarn start` - starts development server
- **Testing**: `yarn test` - runs test suite
- **Linting**: `yarn lint` - checks code style
- **Type Checking**: `yarn flow` - runs Flow type checker

### Production Build
```bash
yarn build:prod
```
This creates optimized production builds in the `build/` directory.

## Code Quality & Organization

### Strengths
- **Excellent Documentation**: Comprehensive README and inline documentation
- **Consistent Code Style**: Enforced through Prettier and ESLint
- **Extensive Testing**: High test coverage with unit and integration tests
- **Modular Architecture**: Clean separation of concerns across packages
- **Performance Focused**: Optimized build process and runtime performance

### Development Practices
- **Conventional Commits**: Standardized commit message format
- **Code Review Process**: All changes go through pull request review
- **Continuous Integration**: Automated testing and builds
- **Semantic Versioning**: Proper version management

## Deployment Options

### NPM Package
React is primarily distributed as NPM packages:
- `react`: Core library
- `react-dom`: DOM renderer
- Various other packages for different use cases

### CDN Usage
```html
<script src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
<script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
```

## Recommendations

### For Contributors
1. **Read Contributing Guide**: Follow the detailed contribution guidelines
2. **Start Small**: Begin with documentation or small bug fixes
3. **Understand Architecture**: Study the modular package structure
4. **Run Tests**: Always ensure tests pass before submitting PRs

### For Users
1. **Use Official Builds**: Prefer NPM packages over building from source
2. **Follow Documentation**: Extensive docs available at reactjs.org
3. **Stay Updated**: Follow React blog for updates and best practices
4. **Performance**: Use production builds for deployment

This repository represents a mature, well-architected JavaScript library with excellent development practices and comprehensive tooling.
```

## 🔮 Future Enhancements

- **Multi-language Support**: Analysis for more programming languages
- **Integration Testing**: Automated testing of analysis accuracy
- **Performance Metrics**: Repository performance and complexity scoring
- **Visual Architecture**: Generate architecture diagrams automatically
- **CI/CD Analysis**: Analyze and recommend CI/CD improvements 