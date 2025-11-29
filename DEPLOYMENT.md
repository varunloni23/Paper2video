# Paper2Video Deployment Guide

This guide covers deploying the Paper2Video application with:
- **Backend**: Render (FastAPI)
- **Frontend**: Vercel (Next.js)
- **Database**: Neon PostgreSQL (already configured)

## Prerequisites

1. GitHub account with your code pushed to a repository
2. Render account (https://render.com)
3. Vercel account (https://vercel.com)
4. Your API keys ready:
   - OpenAI API Key or Gemini API Key
   - Database URL (already have Neon)

---

## Step 1: Push Code to GitHub

```bash
cd /Users/varunloni/Desktop/Paper2video

# Initialize git if not already
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - Paper2Video application"

# Create a new repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/paper2video.git
git branch -M main
git push -u origin main
```

---

## Step 2: Deploy Backend on Render

### 2.1 Create a New Web Service

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Select the `paper2video` repository

### 2.2 Configure the Service

| Setting | Value |
|---------|-------|
| **Name** | `paper2video-api` |
| **Region** | Oregon (US West) or closest to you |
| **Branch** | `main` |
| **Root Directory** | `backend` |
| **Runtime** | Python 3 |
| **Build Command** | `./build.sh` |
| **Start Command** | `uvicorn main:app --host 0.0.0.0 --port $PORT` |
| **Instance Type** | Free (or Starter for better performance) |

### 2.3 Add Environment Variables

Click **"Advanced"** and add these environment variables:

| Key | Value |
|-----|-------|
| `DATABASE_URL` | `postgresql+asyncpg://neondb_owner:npg_Wp3OkPJ7EFxh@ep-fragrant-dust-ahntfjkd-pooler.c-3.us-east-1.aws.neon.tech/neondb?ssl=require` |
| `OPENAI_API_KEY` | Your OpenAI API key |
| `GEMINI_API_KEY` | Your Gemini API key (optional) |
| `FRONTEND_URL` | `https://your-app.vercel.app` (update after Vercel deploy) |
| `ENVIRONMENT` | `production` |
| `PYTHON_VERSION` | `3.11.0` |

### 2.4 Deploy

Click **"Create Web Service"** and wait for the deployment to complete.

Your backend will be available at: `https://paper2video-api.onrender.com`

> ⚠️ **Note**: Free tier services spin down after 15 minutes of inactivity. First request after spin-down takes ~30 seconds.

---

## Step 3: Deploy Frontend on Vercel

### 3.1 Import Project

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click **"Add New..."** → **"Project"**
3. Import your GitHub repository
4. Select the `paper2video` repository

### 3.2 Configure the Project

| Setting | Value |
|---------|-------|
| **Framework Preset** | Next.js |
| **Root Directory** | `frontend` |
| **Build Command** | `npm run build` |
| **Output Directory** | `.next` |
| **Install Command** | `npm install` |

### 3.3 Add Environment Variables

Add the following environment variable:

| Key | Value |
|-----|-------|
| `NEXT_PUBLIC_API_URL` | `https://paper2video-api.onrender.com` |

Replace with your actual Render URL.

### 3.4 Deploy

Click **"Deploy"** and wait for the build to complete.

Your frontend will be available at: `https://paper2video.vercel.app` (or similar)

---

## Step 4: Update CORS Configuration

After both deployments are complete:

1. Go back to Render Dashboard
2. Navigate to your `paper2video-api` service
3. Go to **Environment** tab
4. Update `FRONTEND_URL` with your actual Vercel URL
5. Click **"Save Changes"** - service will redeploy automatically

---

## Step 5: Verify Deployment

### Test Backend Health
```bash
curl https://paper2video-api.onrender.com/health
# Should return: {"status":"healthy","version":"1.0.0"}
```

### Test Frontend
Open your Vercel URL in a browser and try uploading a PDF.

---

## Troubleshooting

### Backend Issues

**Problem**: Service keeps crashing
- Check Render logs for errors
- Ensure all environment variables are set correctly
- Verify DATABASE_URL format is correct

**Problem**: CORS errors
- Ensure FRONTEND_URL in Render matches your Vercel URL exactly
- Include `https://` in the URL

**Problem**: FFmpeg not found
- Render includes FFmpeg by default, but check logs
- May need to use a Docker deployment for custom FFmpeg

### Frontend Issues

**Problem**: API calls fail
- Check browser console for errors
- Verify NEXT_PUBLIC_API_URL is set correctly
- Ensure it starts with `https://`

**Problem**: Build fails
- Check Vercel build logs
- Ensure all dependencies are in package.json

---

## Environment Variables Reference

### Backend (Render)

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | ✅ | PostgreSQL connection string |
| `OPENAI_API_KEY` | ✅ | OpenAI API key for GPT-4 |
| `GEMINI_API_KEY` | ❌ | Google Gemini API key (alternative) |
| `FRONTEND_URL` | ✅ | Vercel frontend URL for CORS |
| `ENVIRONMENT` | ❌ | `production` or `development` |
| `PYTHON_VERSION` | ❌ | Python version (3.11.0 recommended) |

### Frontend (Vercel)

| Variable | Required | Description |
|----------|----------|-------------|
| `NEXT_PUBLIC_API_URL` | ✅ | Render backend URL |

---

## Upgrading to Production

For better performance, consider:

1. **Render Starter Plan** ($7/month): No cold starts
2. **Vercel Pro**: Better build times and bandwidth
3. **Dedicated Database**: Neon Pro for more connections
4. **CDN for Videos**: Use Cloudflare R2 or AWS S3 for video storage

---

## Support

If you encounter issues:
1. Check service logs in Render/Vercel dashboards
2. Verify all environment variables are correct
3. Test API endpoints directly with curl
4. Check browser network tab for failed requests
