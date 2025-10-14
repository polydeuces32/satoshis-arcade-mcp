# Vercel Deployment Guide

## Quick Deploy to Vercel (2 minutes)

### Method 1: Vercel CLI (Recommended)

1. **Install Vercel CLI**:
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```

3. **Deploy**:
   ```bash
   vercel --prod
   ```

### Method 2: Vercel Dashboard (Web)

1. **Go to**: https://vercel.com/new
2. **Import Git Repository**: 
   - Connect GitHub
   - Select `polydeuces32/satoshis-arcade-mcp`
3. **Configure**:
   - Framework Preset: Other
   - Build Command: (leave empty)
   - Output Directory: (leave empty)
4. **Deploy**: Click "Deploy"

### Method 3: GitHub Integration

1. **Go to**: https://vercel.com/new
2. **Import from GitHub**: Select your repository
3. **Auto-deploy**: Vercel will automatically deploy on every push

## Configuration Files

- ✅ `vercel.json`: Vercel configuration
- ✅ `requirements.txt`: Python dependencies
- ✅ `api/__init__.py`: Python package marker

## Benefits of Vercel

- 🚀 **Fast deployment** (30 seconds)
- 🔄 **Auto-deploy** from GitHub
- 🌍 **Global CDN**
- 📱 **Mobile optimized**
- 🔧 **Easy configuration**
- 💰 **Free tier** available

## Your Arcade Will Be Live At

After deployment, your arcade will be available at:
`https://satoshis-arcade-mcp.vercel.app`

## Troubleshooting

If deployment fails:
1. Check `vercel.json` syntax
2. Ensure all dependencies are in `requirements.txt`
3. Verify `api/main.py` exists and is correct
