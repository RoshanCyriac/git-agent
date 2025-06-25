# GitHub Repository Deployment Analyzer

A powerful web-based tool that analyzes GitHub repositories and provides clear **YES/NO** answers about deployment feasibility. Features support for both public and private repositories with GitHub token authentication.

## ✨ Features

- **🔍 Smart Analysis**: Clear YES/NO deployment feasibility answers
- **🔐 Private Repository Support**: Connect with GitHub Personal Access Token
- **🌐 Public Repository Support**: Analyze any public GitHub repository
- **⚙️ Environment Variables**: Easy setup with .env file preview
- **🎯 Deployment Instructions**: Personalized setup commands and requirements
- **🚀 Modern Web Interface**: Real-time analysis with progress tracking
- **🔒 Secure**: GitHub tokens handled securely, stored only in memory

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- OpenRouter API key (for AI analysis)

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd ros
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENROUTER_API_KEY
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Open your browser**
   ```
   http://localhost:5000
   ```

## 🎯 How to Use

### For Public Repositories
1. Enter any GitHub repository URL
2. Configure environment variables (optional)
3. Get instant deployment analysis

### For Private Repositories
1. Click "Private Repository" tab
2. Enter your GitHub Personal Access Token
3. Select from your repositories
4. Configure environment variables
5. Get detailed deployment analysis

## 🔑 GitHub Token Setup

To access private repositories:

1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Generate new token with `repo` scope
3. Copy the token (starts with `ghp_` or `github_pat_`)
4. Paste it in the Private Repository tab

## 📁 Project Structure

```
ros/
├── app.py                 # Main Flask application
├── agent/                 # AI analysis agent
│   ├── __init__.py
│   └── react_agent.py     # ReAct agent implementation
├── templates/             # HTML templates
│   └── index.html         # Main web interface
├── static/                # Static assets
│   ├── css/
│   │   └── custom.css     # Custom styles
│   └── js/
│       └── app.js         # Frontend JavaScript
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── .gitignore            # Git ignore rules
└── README.md             # This file
```

## ⚙️ Environment Variables

Create a `.env` file with:

```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
SECRET_KEY=your_flask_secret_key_here
```

## 🔧 Technical Details

### Backend
- **Flask**: Web framework with SocketIO for real-time updates
- **LangChain**: AI agent framework for repository analysis
- **OpenRouter**: AI model access for analysis

### Frontend
- **Vanilla JavaScript**: No framework dependencies
- **Tailwind CSS**: Utility-first CSS framework
- **Socket.IO**: Real-time communication
- **Font Awesome**: Icons

### AI Analysis
- Uses ReAct (Reasoning and Acting) agent pattern
- Analyzes repository structure, dependencies, and configuration
- Considers user-provided environment variables
- Provides deployment-specific recommendations

## 🚀 Deployment

The application can be deployed on any platform that supports Python Flask applications:

- **Heroku**: Add `Procfile` with `web: python app.py`
- **Railway**: Automatically detects Flask applications
- **Render**: Deploy directly from GitHub
- **DigitalOcean App Platform**: Use Python buildpack

### Environment Variables for Production
```env
OPENROUTER_API_KEY=your_production_api_key
SECRET_KEY=your_production_secret_key
PORT=5000  # Optional, defaults to 5000
```

## 🛠️ Development

### Running in Development Mode
```bash
source venv/bin/activate
python app.py
```

The application runs with debug mode enabled and auto-reloads on file changes.

### Adding New Features
1. Backend logic goes in `app.py`
2. AI agent modifications in `agent/react_agent.py`
3. Frontend updates in `static/js/app.js`
4. Styling changes in `static/css/custom.css`

## 🔒 Security Features

- GitHub tokens stored only in memory during analysis
- Automatic cleanup of cloned repositories
- Input validation and sanitization
- Secure environment variable handling
- No persistent storage of sensitive data

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🆘 Support

If you encounter any issues:
1. Check that your OpenRouter API key is configured correctly
2. Ensure your GitHub token has the correct permissions
3. Verify the repository URL is accessible
4. Check the browser console for JavaScript errors

For additional support, please open an issue on GitHub. 