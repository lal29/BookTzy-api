# BookTzy Deployment Guide

## Overview
- **Frontend** (React/Vite) → Vercel
- **Backend** (FastAPI) → Render
- **Database** (PostgreSQL) → Render

---

## Prerequisites
- GitHub account
- Vercel account (sign in with GitHub)
- Render account (sign in with GitHub)

---

## 1. Prepare the Backend

### Install dependencies and generate requirements.txt
```bash
cd dental-booking-api
venv\Scripts\activate
pip install python-dotenv
pip freeze > requirements.txt
```

### Create .gitignore
```
venv/
__pycache__/
*.pyc
.env
.env.production
frontend/
```

### Setup environment variables (local)
Create a `.env` file in the backend root:
```
DATABASE_URL=postgresql://localhost:5432/your_local_db
```

### Update database.py to load .env
```python
from dotenv import load_dotenv
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
```

### Initialize git and push to GitHub
```bash
git init
git add .
git commit -m "initial commit"
git remote add origin https://github.com/<your-username>/BookTzy-api.git
git push -u origin main
```

---

## 2. Deploy Backend to Render

1. Go to **render.com** → **New** → **Web Service**
2. Connect your `BookTzy-api` GitHub repo
3. Fill in:
   - **Language**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: Free
4. Click **Deploy**

---

## 3. Create PostgreSQL Database on Render

1. Go to Render → **New** → **PostgreSQL**
2. Name it `booktzy-db`, select **Free** tier
3. Click **Create Database**
4. Copy the **Internal Database URL**

### Add DATABASE_URL to Render Web Service
1. Go to your `BookTzy-api` web service → **Environment**
2. Add: `DATABASE_URL` = Internal Database URL from above
3. Save — Render will redeploy automatically

### Run create_tables.py against Render database
1. Temporarily set your local `.env` to the **External Database URL**
2. Run:
```bash
python create_tables.py
python seed.py
```
3. Switch `.env` back to your local database URL

---

## 4. Configure CORS
In `main.py`, add your Vercel URL to allowed origins:
```python
allow_origins=[
    "http://localhost:5173",
    "https://your-app.vercel.app"
]
```
Commit and push to trigger a redeploy on Render.

---

## 5. Prepare the Frontend

### Setup environment variables
Create `.env` in frontend root (for local dev):
```
VITE_API_URL=http://localhost:8000
```

Create `.env.production` (for production build):
```
VITE_API_URL=https://your-api.onrender.com
```

Add both to `.gitignore`:
```
.env
.env.production
```

### Update api/index.js
```js
const API_URL = import.meta.env.VITE_API_URL || "https://your-api.onrender.com";
```

### Initialize git and push to GitHub
```bash
git init
git add .
git commit -m "initial commit"
git remote add origin https://github.com/<your-username>/BookTzy.git
git push -u origin main
```

---

## 6. Deploy Frontend to Vercel

1. Go to **vercel.com** → **Add New Project**
2. Import `BookTzy` GitHub repo
3. Vercel auto-detects Vite/React — click **Deploy**
4. Go to **Settings** → **Environment Variables**
5. Add: `VITE_API_URL` = `https://your-api.onrender.com`
6. Redeploy to apply the environment variable

---

## 7. Ongoing Deployments

- **Frontend**: Every `git push` to `main` auto-deploys to Vercel
- **Backend**: Every `git push` to `main` auto-deploys to Render
- **Database**: Render free PostgreSQL expires after 90 days — recreate and reseed when needed

---

## Useful Commands

### Push frontend changes
```bash
cd frontend/dental-booking-website
git add .
git commit -m "your message"
git push
```

### Push backend changes
```bash
cd dental-booking-api
git add .
git commit -m "your message"
git push
```

### Update requirements.txt (after installing new packages)
```bash
pip freeze > requirements.txt
```

### Remove accidentally committed .env files
```bash
git rm --cached .env
git rm --cached .env.production
git commit -m "remove env files from tracking"
git push
```
