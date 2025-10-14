# Render.com Deployment Guide

## Manual Deployment Steps

### Step 1: Access Render Dashboard
1. Go to [https://dashboard.render.com](https://dashboard.render.com)
2. Sign in with your Render account
3. Click "New +" button
4. Select "Web Service"

### Step 2: Connect GitHub Repository
1. Click "Connect GitHub" if not already connected
2. Authorize Render to access your repositories
3. Select "polydeuces32/satoshis-arcade-mcp" from the list
4. Click "Connect"

### Step 3: Configure Service Settings
- **Name**: `satoshis-arcade-mcp`
- **Branch**: `main`
- **Root Directory**: Leave empty (uses root)
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
- **Plan**: `Free`

### Step 4: Advanced Settings
- **Health Check Path**: `/health`
- **Auto-Deploy**: Enable (checked)
- **Pull Request Previews**: Enable (optional)

### Step 5: Deploy
1. Click "Create Web Service"
2. Wait for deployment to complete (5-10 minutes)
3. Your arcade will be live at: `https://satoshis-arcade-mcp.onrender.com`

## Environment Variables (Optional)
If you need any environment variables, add them in the "Environment" tab:
- `PYTHON_VERSION`: `3.8`
- `PORT`: `10000` (automatically set by Render)

## Monitoring Deployment
1. Go to your service dashboard
2. Check the "Logs" tab for deployment progress
3. Monitor the "Metrics" tab for performance

## Troubleshooting
- **Build Failures**: Check logs for missing dependencies
- **Runtime Errors**: Verify start command is correct
- **Health Check Failures**: Ensure `/health` endpoint is working

## Post-Deployment
1. Test your arcade at the provided URL
2. Check API documentation at `/docs`
3. Monitor performance and logs
4. Set up custom domain if needed

## API Key Usage
Your Render API key: `rnd_IfLkNEeR0FHx4nzccAfwPd51axvY`

This can be used for:
- CLI deployments (if configured)
- API-based service management
- Automated deployments

## Success Indicators
- ✅ Service shows "Live" status
- ✅ Health check returns 200 OK
- ✅ Arcade loads in browser
- ✅ Games are playable
- ✅ AI learning system works
