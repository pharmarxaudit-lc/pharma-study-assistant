# Replit Deployment Guide

This guide will walk you through deploying the Pharmacy Study Assistant application to Replit.

## Prerequisites

- A Replit account (free or paid)
- Your Anthropic API key for Claude integration
- This repository pushed to GitHub

## Step-by-Step Deployment

### 1. Create New Repl from GitHub

1. Go to [Replit](https://replit.com)
2. Click "Create Repl"
3. Select "Import from GitHub"
4. Paste your repository URL: `https://github.com/YOUR_USERNAME/pharma-study-assistant`
5. Replit will automatically detect it's a Python project

### 2. Configure Environment Variables

1. In your Repl, click on "Tools" in the left sidebar
2. Click on "Secrets" (or look for the lock icon)
3. Add the following secret:
   - Key: `ANTHROPIC_API_KEY`
   - Value: Your Anthropic API key (starts with `sk-ant-`)
4. Click "Add Secret"

### 3. Database Setup

The application uses SQLite which is already configured. The database will be created automatically on first run in the `backend/` directory.

### 4. Initial Data Load

If you have existing questions in the database, make sure the `backend/exam_questions.db` file is committed to your repository. If starting fresh, you'll need to run the PDF processing workflow first.

### 5. Run the Application

1. Click the "Run" button at the top of the Repl
2. Replit will:
   - Install dependencies from `requirements.txt`
   - Start the Flask server on port 5001
3. The application should be accessible via the webview on the right side

### 6. Access Your Application

Once running, you can access your app:
- **Webview**: Shown automatically in Replit's right panel
- **Public URL**: Click "Open in new tab" to get a shareable URL
- The URL will be in format: `https://pharma-study-assistant.YOUR_USERNAME.repl.co`

### 7. Deploy to Production (Optional)

For a production deployment with always-on hosting:

1. Click "Deploy" button in Replit
2. Choose deployment type:
   - **Autoscale**: Automatic scaling based on traffic (recommended)
   - **Reserved VM**: Dedicated resources
3. Follow the deployment wizard
4. Your app will get a permanent URL

## Troubleshooting

### Application Won't Start

- Check the Console tab for error messages
- Verify `ANTHROPIC_API_KEY` is set correctly in Secrets
- Make sure all dependencies installed: check the Packages tab

### Database Errors

- Ensure `backend/` directory exists
- Check file permissions in the Shell tab: `ls -la backend/`
- The database will be created automatically if missing

### API Connection Issues

- Verify your Anthropic API key is valid
- Check that you have API credits remaining
- Look for error messages in the backend logs

### Frontend Not Loading

- Make sure `backend/static/` directory contains the built frontend files
- If missing, you may need to build the frontend locally and push to GitHub:
  ```bash
  cd frontend
  npm install
  npm run build
  cp -r dist/* ../backend/static/
  git add backend/static
  git commit -m "Add frontend build"
  git push
  ```

## File Structure for Replit

```
pharma-study-assistant/
├── .replit              # Replit configuration
├── replit.nix           # Nix environment setup
├── requirements.txt     # Python dependencies
├── backend/
│   ├── app.py          # Main Flask application (entry point)
│   ├── requirements.txt # Backend dependencies
│   ├── exam_questions.db # SQLite database
│   └── static/         # Frontend build output
├── frontend/           # Vue.js source (not used in production)
└── uploads/            # PDF upload directory
```

## Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | Yes | Your Claude API key from Anthropic |
| `PORT` | No | Server port (default: 5001, auto-set by Replit) |
| `FLASK_ENV` | No | Flask environment (default: production) |

## Features Available After Deployment

Once deployed, users can:
- ✅ Start practice exams with configurable settings
- ✅ Answer multiple-choice questions
- ✅ View results and performance statistics
- ✅ Review exam history
- ✅ Study from past sessions with detailed explanations
- ✅ Filter and analyze correct/incorrect answers

## Updating the Application

To update your deployed app:

1. Make changes locally and commit to GitHub:
   ```bash
   git add .
   git commit -m "Your update message"
   git push
   ```

2. In Replit, click the "Pull" button or use the Shell:
   ```bash
   git pull
   ```

3. Replit will automatically restart the application

## Support

For issues or questions:
- Check the [GitHub Issues](https://github.com/YOUR_USERNAME/pharma-study-assistant/issues)
- Review application logs in Replit Console
- Verify all environment variables are set correctly

## Security Notes

- Never commit your `.env` file or `ANTHROPIC_API_KEY` to GitHub
- Use Replit Secrets for all sensitive configuration
- The SQLite database may contain user data - handle appropriately
- Consider adding authentication if deploying publicly

---

**Last Updated**: 2025-10-16
**Replit Configuration Version**: 1.0
