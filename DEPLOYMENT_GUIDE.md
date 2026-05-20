# Kaizer News - Railway Deployment Guide (Separate Services)

## You need 3 services in Railway:
1. **Backend** (FastAPI)
2. **Frontend** (React)
3. **MongoDB** (Database)

---

## Step 1: Create Railway Project
1. Go to **[railway.app](https://railway.app)** → Login with GitHub
2. Click **"New Project"** → **"Empty Project"**

## Step 2: Add MongoDB
1. Click **"+ New"** → **"Database"** → **"MongoDB"**
2. Click on MongoDB service → **Variables** tab → Copy `MONGO_URL`

## Step 3: Deploy Backend
1. Click **"+ New"** → **"GitHub Repo"** → Select your repo
2. Click on the service → **Settings**:
   - **Service Name**: `kaizer-backend`
   - **Root Directory**: `backend`
   - **Builder**: Dockerfile
3. **Variables** tab → Add:
   ```
   MONGO_URL = <paste from Step 2>
   DB_NAME = kaizer_news
   EMERGENT_LLM_KEY = <your key>
   AUTHKEY_API_KEY = <your key>
   IMAGEKIT_PRIVATE_KEY = <your key>
   IMAGEKIT_PUBLIC_KEY = <your key>
   IMAGEKIT_URL_ENDPOINT = <your url>
   PORT = 8001
   ```
4. **Settings** → **Networking** → **"Generate Domain"**
5. Note the URL (e.g. `kaizer-backend-xxx.up.railway.app`)

## Step 4: Deploy Frontend
1. Click **"+ New"** → **"GitHub Repo"** → Select the SAME repo again
2. Click on this service → **Settings**:
   - **Service Name**: `kaizer-frontend`
   - **Root Directory**: `frontend`
   - **Builder**: Dockerfile
3. **Variables** tab → Add:
   ```
   REACT_APP_BACKEND_URL = https://kaizer-backend-xxx.up.railway.app
   PORT = 3000
   ```
   *(Use the backend URL from Step 3.5)*
4. **Settings** → **Networking** → **"Generate Domain"**

## Step 5: Update Backend CORS
1. Go to Backend service → **Variables**
2. Add: `CORS_ORIGINS = https://kaizer-frontend-xxx.up.railway.app`

## Step 6: Connect GoDaddy Domain (Optional)
1. In Railway → Frontend service → **Settings** → **Networking**
2. Click **"+ Custom Domain"** → Enter your domain
3. Railway shows a **CNAME** record
4. Go to GoDaddy → DNS Management → Add CNAME record
5. Wait 5-30 min for DNS → Railway auto-provisions HTTPS
6. Update `CORS_ORIGINS` in backend to include your custom domain

---

## Troubleshooting
| Issue | Fix |
|-------|-----|
| Backend build fails | Check Root Directory = `backend` |
| Frontend build fails | Check Root Directory = `frontend` |
| CORS errors | Add frontend URL to `CORS_ORIGINS` in backend variables |
| MongoDB connection failed | Check `MONGO_URL` is from Railway's MongoDB |
| Frontend API calls fail | Check `REACT_APP_BACKEND_URL` points to backend domain |
