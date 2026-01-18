# 🚀 LIVE Deployment Guide - Phishing Detection App

## Quick Deployment (Recommended: Render + Vercel)

This guide will help you deploy your phishing detection app to **free** hosting services:
- **Backend**: Render.com (Free tier - 512MB RAM)
- **Frontend**: Vercel (Free tier - unlimited)

---

## 📦 STEP 1: Push Code to GitHub

First, create a GitHub repository and push your code:

```bash
# Initialize git (if not done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - Phishing Detection App"

# Create repo on GitHub and add remote
git remote add origin https://github.com/YOUR_USERNAME/phishing-detection.git

# Push
git branch -M main
git push -u origin main
```

---

## 🔧 STEP 2: Deploy Backend to Render.com

### 2.1 Sign Up & Create Service

1. Go to **https://render.com** and sign up (use GitHub for easy setup)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository

### 2.2 Configure the Service

Fill in these settings:

| Setting | Value |
|---------|-------|
| **Name** | `phishing-detection-api` |
| **Region** | Oregon (US West) |
| **Branch** | `main` |
| **Root Directory** | (leave empty) |
| **Runtime** | Python 3 |
| **Build Command** | `pip install -r requirements-render.txt` |
| **Start Command** | `cd backend && python -m uvicorn main:app --host 0.0.0.0 --port $PORT` |
| **Instance Type** | Free |

### 2.3 Add Environment Variables

Click **"Advanced"** and add these environment variables:

```
ENVIRONMENT=production
DEBUG=false
HOST=0.0.0.0
LOG_LEVEL=INFO
MODEL_DEVICE=cpu
```

### 2.4 Deploy!

Click **"Create Web Service"** - deployment takes 5-10 minutes.

Your backend URL will be: `https://phishing-detection-api.onrender.com`

**⚠️ Note**: Free tier sleeps after 15 min of inactivity. First request may take 30-60 seconds to wake up.

---

## 🎨 STEP 3: Deploy Frontend to Vercel

### 3.1 Sign Up & Import Project

1. Go to **https://vercel.com** and sign up with GitHub
2. Click **"Add New Project"**
3. Import your GitHub repository

### 3.2 Configure Build Settings

| Setting | Value |
|---------|-------|
| **Framework Preset** | Vite |
| **Root Directory** | `frontend` |
| **Build Command** | `npm run build` |
| **Output Directory** | `dist` |

### 3.3 Add Environment Variable

Add this environment variable:

```
VITE_API_URL=https://phishing-detection-api.onrender.com
```

(Replace with your actual Render backend URL from Step 2)

### 3.4 Deploy!

Click **"Deploy"** - takes 1-2 minutes.

Your frontend URL will be: `https://your-project-name.vercel.app`

---

## ✅ STEP 4: Verify Deployment

### Test Backend API
Open in browser: `https://phishing-detection-api.onrender.com/health`

You should see:
```json
{
  "status": "healthy",
  "models_loaded": true,
  "version": "1.0.0"
}
```

### Test Frontend
Open your Vercel URL and try scanning a URL!

---

## 🔄 Alternative: Deploy Both to Render

You can also deploy the frontend to Render as a static site:

1. **New +** → **Static Site**
2. Connect GitHub repo
3. Settings:
   - **Root Directory**: `frontend`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `dist`
4. Add environment variable: `VITE_API_URL=https://your-backend.onrender.com`

---

## 🐳 Alternative: Deploy with Docker (Railway)

### Railway Deployment

1. Go to **https://railway.app** and sign up with GitHub
2. Click **"Deploy from GitHub repo"**
3. Select your repository
4. Railway auto-detects the Dockerfile
5. Add environment variables:
   ```
   PORT=8000
   ENVIRONMENT=production
   MODEL_DEVICE=cpu
   ```

---

## 🔧 Troubleshooting

### Backend Issues

**"Application Error" on Render**
- Check logs in Render dashboard
- Ensure `requirements-render.txt` is correct
- Verify start command is correct

**Models not loading**
- Free tier has limited memory (512MB)
- Models load on first request
- First prediction may be slow

### Frontend Issues

**API calls failing**
- Check `VITE_API_URL` is set correctly
- Verify backend is running (check `/health`)
- Check browser console for CORS errors

**Build failing on Vercel**
- Ensure root directory is set to `frontend`
- Check `package.json` has all dependencies

---

## 📊 Free Tier Limits

### Render.com (Backend)
- 512 MB RAM
- Shared CPU
- Sleeps after 15 min inactivity
- 750 hours/month free

### Vercel (Frontend)
- Unlimited static sites
- 100 GB bandwidth/month
- Automatic HTTPS
- Global CDN

---

## 🎉 Your Live URLs

After deployment, you'll have:

| Service | URL |
|---------|-----|
| **Backend API** | `https://phishing-detection-api.onrender.com` |
| **Frontend App** | `https://your-app.vercel.app` |
| **API Docs** | `https://phishing-detection-api.onrender.com/docs` |
| **Health Check** | `https://phishing-detection-api.onrender.com/health` |

---

## 🔐 Security Notes for Production

1. Update CORS in `backend/config/settings.py`:
   ```python
   CORS_ORIGINS: List[str] = ["https://your-app.vercel.app"]
   ```

2. Consider adding rate limiting for production use

3. Monitor your usage on both platforms

---

**Need help?** Check the logs in your Render/Vercel dashboard for error details.
