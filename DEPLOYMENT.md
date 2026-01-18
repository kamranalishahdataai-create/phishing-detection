# NABIH Phishing Detection - Deployment Guide

## 🚀 Quick Start Deployment

### Option 1: Railway (Recommended for Backend)

1. **Sign up** at https://railway.app
2. **Connect GitHub** and push your code
3. **Create New Project** → Deploy from GitHub
4. Railway auto-detects Python and deploys!

### Option 2: Render (Free Tier)

1. Sign up at https://render.com
2. Create "New Web Service"
3. Connect your GitHub repo
4. Set:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

### Option 3: Vercel (Frontend Only)

1. Sign up at https://vercel.com
2. Import your GitHub repo
3. Set root directory to `frontend`
4. Deploy!

---

## 📁 File Structure for Deployment

```
phishing_detection/
├── backend/                 # Deploy to Railway/Render
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── railway.json
│   └── ...
├── frontend/                # Deploy to Vercel/Netlify
│   ├── vercel.json
│   ├── package.json
│   └── ...
└── docker-compose.yml       # For self-hosted
```

---

## 🔧 Environment Variables

### Backend (.env)
```
ENVIRONMENT=production
DEBUG=false
HOST=0.0.0.0
PORT=8000
DATABASE_URL=sqlite:///./phishing.db
```

### Frontend (.env.production)
```
VITE_API_URL=https://your-backend-url.railway.app
```

---

## 🐳 Docker Deployment (Self-Hosted)

```bash
# Build and run with Docker Compose
docker-compose up -d
```

---

## 🌐 Chrome Web Store (Extension)

To publish as a Chrome Extension:

1. Build the extension: `npm run build:extension`
2. Create developer account: https://chrome.google.com/webstore/devconsole
3. Pay $5 one-time fee
4. Upload ZIP file
5. Submit for review (1-3 days)

---

## 🔒 Production Checklist

- [ ] Set `DEBUG=false`
- [ ] Configure CORS for your domain
- [ ] Set up SSL/HTTPS
- [ ] Add rate limiting
- [ ] Configure database (PostgreSQL recommended)
- [ ] Set up monitoring (Sentry, LogRocket)
- [ ] Add API authentication
