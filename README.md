# GitHub Repository Deployment Analyzer

🚀 **Analyze any GitHub repository and get comprehensive deployment information with a single command!**

This tool uses AI to analyze GitHub repositories and provide detailed deployment guides, including setup instructions, dependencies, configuration requirements, and step-by-step deployment strategies.

## Quick Start

```bash
# 1. Set up the environment
git clone <this-repo>
cd ros
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Add your API key to .env file
cp .env.example .env
# Edit .env and add your OPENROUTER_API_KEY

# 3. Analyze any GitHub repository
python analyze_repo.py https://github.com/tiangolo/fastapi
```

## What You Get

The tool provides comprehensive analysis including:

- 📋 **Essential Files & Documentation** - README analysis, package files, documentation structure
- ⚙️ **Configuration & Environment** - Environment variables, database requirements, runtime needs  
- 🚀 **Deployment Files** - Docker configs, CI/CD workflows, server configurations
- 🏗️ **Architecture & Build** - Project structure, build processes, testing procedures
- 📝 **Step-by-Step Instructions** - Complete deployment guide from setup to production

## Usage

```bash
# Activate virtual environment
source venv/bin/activate

# Analyze any GitHub repository
python analyze_repo.py <github_url>
```

### Examples

```bash
# Simple repository
python analyze_repo.py https://github.com/octocat/Hello-World

# Complex web application  
python analyze_repo.py https://github.com/tiangolo/fastapi

# Large enterprise project
python analyze_repo.py https://github.com/microsoft/vscode

# Frontend framework
python analyze_repo.py https://github.com/facebook/create-react-app
```

## Sample Output

```
🔍 Analyzing repository: https://github.com/tiangolo/fastapi
⏳ Analyzing deployment requirements...

================================================================================
🚀 DEPLOYMENT ANALYSIS RESULTS  
================================================================================
📁 Repository: https://github.com/tiangolo/fastapi
🧠 Model: anthropic/claude-3-5-sonnet-20241022

📋 Comprehensive Deployment Guide:
--------------------------------------------------------------------------------

# FastAPI Deployment Guide

## ESSENTIAL FILES & DOCUMENTATION
- README.md: Comprehensive documentation with installation and usage
- requirements.txt: Python dependencies
- pyproject.toml: Modern Python packaging configuration
...

## CONFIGURATION & ENVIRONMENT  
- Python 3.7+ required
- Optional dependencies for specific features
- Environment variables for configuration
...

[Full detailed analysis with step-by-step instructions]
```

## Requirements

- Python 3.7+
- OpenRouter API Key ([get one here](https://openrouter.ai/))
- Git installed

## API Key Setup

1. Visit [OpenRouter](https://openrouter.ai/)
2. Sign up and generate an API key
3. Copy `.env.example` to `.env`
4. Add your API key: `OPENROUTER_API_KEY=your_key_here`

## Troubleshooting

**"ModuleNotFoundError"**: Make sure virtual environment is activated and dependencies installed
```bash
source venv/bin/activate
pip install -r requirements.txt
```

**"API key not found"**: Check your `.env` file has the correct API key

**Analysis takes long**: Large repositories may take several minutes - this is normal

## Project Structure

```
├── analyze_repo.py          # Main command-line tool
├── requirements.txt         # Dependencies  
├── .env.example            # API key template
├── agent/                  # ReAct agent implementation
└── tools/                  # Repository analysis tools
```

## How It Works

The tool uses a ReAct (Reasoning and Acting) AI agent that:
1. Clones the GitHub repository
2. Analyzes the project structure and key files
3. Generates comprehensive deployment instructions
4. Automatically cleans up temporary files

---

**Made with ❤️ using LangChain ReAct Framework and OpenRouter AI** 