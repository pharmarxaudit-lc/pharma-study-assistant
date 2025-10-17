# Replit Deployment Guide

Complete guide for deploying the Pharmacy Study Assistant full-stack application (Flask + Vue.js) to Replit.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Project Structure](#project-structure)
4. [Configuration Files](#configuration-files)
5. [Environment Variables & Secrets](#environment-variables--secrets)
6. [Build & Deployment](#build--deployment)
7. [Post-Deployment Setup](#post-deployment-setup)
8. [Troubleshooting](#troubleshooting)
9. [Updating the Application](#updating-the-application)

---

## Prerequisites

- Replit account (free or paid)
- Anthropic API key for Claude integration
- Repository on GitHub (recommended) or project files ready to upload

---

## Quick Start

### 1. Create New Repl from GitHub

1. Go to [Replit](https://replit.com)
2. Click "Create Repl"
3. Select "Import from GitHub"
4. Paste your repository URL
5. Replit will automatically detect it's a Python project

### 2. Configure Secrets

1. Click "Tools" → "Secrets" (or the lock icon 🔒)
2. Add your API key:
   - Key: `ANTHROPIC_API_KEY`
   - Value: Your Anthropic API key (starts with `sk-ant-`)

### 3. Build & Run

The application will automatically build the frontend and start the backend when you click "Run".

---

## Project Structure

```
pharma-study-assistant/
├── backend/
│   ├── app.py                 # Flask app (main entry point)
│   ├── pdf_extractor.py
│   ├── text_processor.py
│   ├── content_analyzer.py
│   ├── llm_formatter.py
│   ├── database.py
│   ├── database_models.py
│   ├── config.py
│   └── pharma_exam.db        # SQLite database (auto-created)
├── frontend/
│   ├── src/                  # Vue.js source
│   ├── public/
│   ├── dist/                 # Build output (generated)
│   ├── package.json
│   ├── vite.config.ts
│   └── tsconfig.json
├── requirements.txt          # Python dependencies
├── .replit                   # Replit configuration
├── replit.nix                # Nix environment
└── uploads/                  # PDF uploads (auto-created)
```

---

## Configuration Files

### `.replit` Configuration

Update your `.replit` file for full-stack deployment:

```toml
run = "sh -c 'cd frontend && npm install && npm run build && cd .. && python backend/app.py'"
entrypoint = "backend/app.py"
language = "python3"

[nix]
channel = "stable-22_11"

[deployment]
run = ["sh", "-c", "cd frontend && npm run build && cd .. && python backend/app.py"]
build = ["sh", "-c", "cd frontend && npm install && npm run build"]
deploymentTarget = "cloudrun"

[env]
PORT = "5000"
FLASK_ENV = "production"
NODE_ENV = "production"
```

### `replit.nix` Configuration

Ensure both Python and Node.js are available:

```nix
{ pkgs }: {
  deps = [
    pkgs.python310
    pkgs.python310Packages.pip
    pkgs.nodejs-18_x
    pkgs.nodePackages.npm
  ];
}
```

### Python Dependencies

Your `requirements.txt`:

```
flask==3.0.0
flask-cors==4.0.0
PyMuPDF==1.23.8
anthropic>=0.25.0
python-dotenv==1.0.0
sqlalchemy==2.0.23
```

---

## Environment Variables & Secrets

### Required Secrets (Replit Secrets Panel)

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | ✅ Yes | Claude API key from Anthropic |
| `FLASK_SECRET_KEY` | Optional | Random string for sessions (auto-generated if not set) |
| `DEBUG` | Optional | Set to `False` for production |

**How to Add Secrets:**

1. Click lock icon 🔒 in left sidebar
2. Click "Add Secret"
3. Enter key and value
4. Click "Add Secret"

### Environment Variables in `.replit`

Set in the `[env]` section:

```toml
[env]
PORT = "5000"              # Auto-set by Replit if not specified
FLASK_ENV = "production"
NODE_ENV = "production"
```

**Note:** Replit automatically sets `REPLIT_DEPLOYMENT=true` when deployed.

---

## Build & Deployment

### Method 1: Development Run (Testing in Replit)

1. Click the "Run" button
2. Replit will:
   - Install Python dependencies
   - Install Node dependencies
   - Build Vue.js frontend
   - Start Flask backend
3. Access via webview panel

### Method 2: Production Deployment

#### Reserved VM Deployment (Recommended)

1. Click "Deploy" button (🚀 rocket icon)
2. Choose "Reserved VM"
3. Configure:
   - **Build Command:** `cd frontend && npm install && npm run build`
   - **Run Command:** `python backend/app.py`
4. Click "Deploy"
5. Access at: `https://<your-subdomain>.replit.app`

#### Autoscale Deployment

For variable traffic:

1. Choose "Autoscale Deployment"
2. Same build/run commands
3. Set min/max instances as needed

### Build Script (Recommended)

Create `start.sh` in root directory:

```bash
#!/bin/bash
set -e

echo "Building frontend..."
cd frontend
npm install
npm run build
cd ..

echo "Starting Flask backend..."
python backend/app.py
```

Make executable:

```bash
chmod +x start.sh
```

Update `.replit`:

```toml
run = "./start.sh"
```

---

## Post-Deployment Setup

### 1. Update Flask Static Folder

**In `backend/app.py`, update line 32:**

```python
# Change from:
app = Flask(__name__, static_folder='static', static_url_path='')

# To:
app = Flask(__name__, static_folder='../frontend/dist', static_url_path='')
```

This serves the built Vue.js frontend from the Flask backend.

### 2. Verify Frontend Build

Check that `frontend/dist/` contains:

```
dist/
├── index.html
├── assets/
│   ├── index-*.js
│   └── index-*.css
└── ...
```

### 3. Configure Frontend API Base URL

In your Vue.js app (e.g., `frontend/src/config.ts` or main API file):

```typescript
// For Replit deployment
const apiBaseUrl = import.meta.env.PROD
  ? '/api'  // Production: same origin
  : 'http://localhost:5000/api';  // Development

export default apiBaseUrl;
```

### 4. Database Initialization

The SQLite database is created automatically on first run. Location: `backend/pharma_exam.db`

If you need to initialize manually:

```bash
python backend/init_database.py
```

### 5. Access Your Application

**Development URL:**
- Via Replit webview panel

**Production URL:**
- `https://<your-repl-name>.replit.app`
- Or custom subdomain: `https://<subdomain>.replit.app`

---

## Troubleshooting

### Issue 1: Application Won't Start

**Symptoms:** Error messages in console

**Solutions:**
- Check Console tab for specific errors
- Verify `ANTHROPIC_API_KEY` is set in Secrets
- Check Packages tab - dependencies should be installed
- Run manually: `pip install -r requirements.txt`

### Issue 2: Frontend Not Building

**Symptoms:** Missing `dist/` folder or build errors

**Solutions:**

```bash
# Check Node.js version
node --version
npm --version

# Rebuild frontend manually
cd frontend
rm -rf node_modules dist
npm install
npm run build
```

### Issue 3: Static Files Not Serving

**Symptoms:** Blank page or 404 errors

**Solutions:**

1. Verify Flask static folder in `backend/app.py`:

```python
print(f"Static folder: {app.static_folder}")
print(f"Static folder exists: {os.path.exists(app.static_folder)}")
```

2. Check `frontend/dist/index.html` exists:

```bash
ls -la frontend/dist/
```

3. Ensure Flask route serves index:

```python
@app.route('/')
def index():
    return app.send_static_file('index.html')
```

### Issue 4: Module Not Found Errors

**Symptoms:** `ModuleNotFoundError` in console

**Solutions:**

```bash
# Add missing packages via UPM (Replit's package manager)
upm add flask==3.0.0
upm add flask-cors==4.0.0
upm add PyMuPDF==1.23.8
upm add 'anthropic>=0.25.0'
upm add python-dotenv==1.0.0
upm add sqlalchemy==2.0.23

# Or use pip
pip install -r requirements.txt
```

### Issue 5: Database Errors

**Symptoms:** SQLAlchemy errors or missing database

**Solutions:**

```bash
# Check database exists
ls -la backend/pharma_exam.db

# Initialize database
python backend/init_database.py

# Check permissions
chmod 644 backend/pharma_exam.db
```

### Issue 6: Port Conflicts

**Symptoms:** Port already in use

**Solution:**

Replit auto-assigns ports. Ensure your app reads from environment:

```python
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
```

### Issue 7: CORS Errors

**Symptoms:** Browser console shows CORS policy errors

**Solution:**

Ensure CORS is configured in `backend/app.py`:

```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
```

### Issue 8: API Connection Issues

**Symptoms:** Claude API errors

**Solutions:**
- Verify API key is valid (check Anthropic dashboard)
- Ensure you have API credits remaining
- Check backend logs for specific error messages
- Test API key separately:

```python
import anthropic
client = anthropic.Anthropic(api_key="your-key")
# Try a simple request
```

---

## Updating the Application

### Update from GitHub

1. Make changes locally and push to GitHub:

```bash
git add .
git commit -m "Your update message"
git push
```

2. In Replit, pull changes:
   - Click "Pull" button in Git panel
   - Or use Shell: `git pull`

3. Replit will automatically restart

### Manual Updates in Replit

1. Edit files directly in Replit editor
2. Click "Run" to restart
3. For production, redeploy via Deploy panel

---

## Advanced Configuration

### Custom Domain

1. Go to Deployments → Settings
2. Add custom domain
3. Configure DNS records as instructed by Replit

### Response Headers

Add to `.replit` for CORS configuration:

```toml
[[deployment.responseHeaders]]
path = "/*"
name = "Access-Control-Allow-Origin"
value = "*"
```

### URL Rewrites (SPA Routing)

For Vue Router history mode, add to `.replit`:

```toml
[[deployment.rewrites]]
from = "/*"
to = "/index.html"
```

**Note:** Existing files will "shadow" rewrites (served directly instead).

---

## Features Available After Deployment

Once deployed, users can:

- ✅ Upload PDF pharmacy law materials
- ✅ Process documents with AI-powered topic extraction
- ✅ Generate practice questions automatically
- ✅ Start customized practice exams
- ✅ Answer multiple-choice questions
- ✅ View detailed explanations and key terms
- ✅ Track performance statistics
- ✅ Review exam history
- ✅ Filter questions by topic, difficulty, type
- ✅ Study from past sessions with analytics

---

## Testing Checklist

Before deploying to production:

- [ ] All Python dependencies in `requirements.txt`
- [ ] All Node dependencies in `frontend/package.json`
- [ ] `ANTHROPIC_API_KEY` set in Replit Secrets
- [ ] Frontend builds successfully: `cd frontend && npm run build`
- [ ] Backend serves from `../frontend/dist`
- [ ] Database initializes: `python backend/init_database.py`
- [ ] Health check responds: `curl /api/health`
- [ ] File uploads work
- [ ] Question generation works
- [ ] Practice exams function correctly

---

## Security Notes

- ⚠️ Never commit `.env` file or API keys to GitHub
- ⚠️ Always use Replit Secrets for sensitive configuration
- ⚠️ SQLite database may contain user data - handle appropriately
- ⚠️ Consider adding authentication for public deployments
- ⚠️ Set `FLASK_ENV=production` for production deployments

---

## Support & Resources

**Replit Documentation:**
- [Replit Deployments](https://docs.replit.com/cloud-services/deployments)
- [Flask on Replit](https://docs.replit.com/tutorials/python/build-with-flask)
- [Environment Variables](https://docs.replit.com/replit-workspace/workspace-features/secrets)

**Project Resources:**
- Check application logs in Replit Console
- Review backend logs: `logs/backend.log`
- Verify environment variables in Secrets panel

---

## Quick Reference Commands

```bash
# Build frontend
cd frontend && npm install && npm run build && cd ..

# Initialize database
python backend/init_database.py

# Run application
python backend/app.py

# Test health endpoint
curl http://localhost:5000/api/health

# Check Python packages
pip list

# Check Node packages
cd frontend && npm list
```

---

**Last Updated:** 2025-10-17
**Configuration Version:** 2.0
**Generated with:** Context7 MCP & Claude Code
