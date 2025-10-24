#!/bin/bash

# Replit Deployment Script
# Automatically discards local changes, pulls from GitHub, and redeploys

set -e  # Exit on error

REPLIT_SSH="2c5741f6-a81c-4e09-a04e-a5b21f62c6a2@2c5741f6-a81c-4e09-a04e-a5b21f62c6a2-00-14qfmt95wrr5m.spock.replit.dev"
SSH_KEY="~/.ssh/id_ed25519"

echo "🚀 Starting deployment to Replit..."
echo ""

# Execute commands on Replit
ssh -i $SSH_KEY -p 22 $REPLIT_SSH << 'ENDSSH'
set -e

echo "📂 Current directory: $(pwd)"
echo ""

echo "🔄 Discarding local changes..."
git reset --hard HEAD
git clean -fd
echo "✅ Local changes discarded"
echo ""

echo "📥 Pulling latest changes from GitHub..."
git pull origin main
echo "✅ Git pull completed"
echo ""

echo "🏗️  Building frontend..."
cd frontend
npm install
npm run build
echo "✅ Frontend build completed"
echo ""

echo "📦 Copying build to backend static..."
cd ..
mkdir -p backend/static
rm -rf backend/static/*
cp -r frontend/dist/* backend/static/
echo "✅ Static files copied"
echo ""

echo "🔄 Replit will auto-detect changes and redeploy..."
echo "✅ Deployment preparation complete!"

ENDSSH

echo ""
echo "✨ Deployment script finished!"
echo "🌐 Check your Replit deployment status in the Deployments tab"
