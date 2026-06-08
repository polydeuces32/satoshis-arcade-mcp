# Railway Deployment (Alternative Free Hosting)

## Quick Deploy to Railway

1. Go to: https://railway.app
2. Sign up with GitHub
3. Click "Deploy from GitHub repo"
4. Select: `polydeuces32/satoshis-arcade-mcp`
5. Railway will auto-detect Python and deploy
6. Your arcade will be live in 3-5 minutes!

## Railway Settings (if needed)
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
- **Environment**: Python 3.8+

## Benefits of Railway
- ✅ Free tier available
- ✅ Auto-deployment from GitHub
- ✅ Better API than Render
- ✅ Faster deployment
- ✅ Custom domains
