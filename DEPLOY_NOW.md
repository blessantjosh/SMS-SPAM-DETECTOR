# 🚀 DEPLOY NOW - Step by Step Guide

## ✅ FIXED! Ready to Deploy Properly

The previous deployment failed because we tried to deploy both frontend and backend together on Vercel. 

**New Strategy: Deploy Separately**
- Backend → Railway (Python support)
- Frontend → Vercel (Static files)

---

## 📋 STEP 1: Deploy Backend to Railway (5 minutes)

### 1.1 Go to Railway
Visit: **https://railway.app**

### 1.2 Sign Up / Login
- Click "Login with GitHub"
- Authorize Railway

### 1.3 Create New Project
- Click "New Project"
- Select "Deploy from GitHub repo"
- Choose: **SMS-SPAM-DETECTOR**
- Click "Deploy Now"

### 1.4 Configure Backend Service
Railway will auto-detect Python. Add these settings:

**Start Command:**
```bash
cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
```

**Environment Variables:**
```
PYTHONPATH=/app/src
PORT=8000
```

### 1.5 Wait for Deployment
- Railway will build and deploy (2-3 minutes)
- You'll get a URL like: `https://sms-spam-detector-production.up.railway.app`

### 1.6 Test Backend
Click the URL and add `/api/health`:
```
https://your-backend-url.railway.app/api/health
```

You should see: `{"status":"healthy",...}`

✅ **Backend Deployed!** Copy your backend URL.

---

## 📋 STEP 2: Update Frontend with Backend URL (2 minutes)

### 2.1 Update Environment File
Edit: `cybersentinel-dashboard/src/environments/environment.prod.ts`

Replace with YOUR Railway URL:
```typescript
export const environment = {
  production: true,
  apiUrl: 'https://your-backend-url.railway.app/api'  // ← Paste your Railway URL here
};
```

### 2.2 Update Backend CORS
Edit: `backend/main.py`

Find this line (around line 32):
```python
allow_origins=["http://localhost:4200", "http://localhost:4201", "http://127.0.0.1:4200"],
```

Add your Vercel domain (we'll get it in next step, but add placeholder):
```python
allow_origins=[
    "http://localhost:4200",
    "http://localhost:4201", 
    "http://127.0.0.1:4200",
    "https://*.vercel.app",  # ← Add this
    "https://cybersentinel-ai.vercel.app"  # ← Your custom domain
],
```

---

## 📋 STEP 3: Deploy Frontend to Vercel (3 minutes)

### 3.1 Go to Vercel
Visit: **https://vercel.com**

### 3.2 Sign Up / Login
- Click "Sign Up" or "Login"
- Choose "Continue with GitHub"
- Authorize Vercel

### 3.3 Import Project
- Click "Add New..." → "Project"
- Find: **SMS-SPAM-DETECTOR**
- Click "Import"

### 3.4 Configure Build Settings

**Framework Preset:** Angular

**Root Directory:** `cybersentinel-dashboard`

**Build Command:**
```bash
npm install && npm run build
```

**Output Directory:**
```
dist/cybersentinel-dashboard/browser
```

**Install Command:**
```bash
npm install
```

### 3.5 Deploy
- Click "Deploy"
- Wait 2-3 minutes

### 3.6 Get Your URL
You'll get a URL like:
```
https://cybersentinel-ai-xyz123.vercel.app
```

✅ **Frontend Deployed!**

---

## 📋 STEP 4: Update CORS (Important!)

### 4.1 Copy Your Vercel URL
From the deployment, copy the full URL.

### 4.2 Update Backend CORS
Go back to Railway dashboard:
- Open your backend project
- Go to "Variables" tab
- Add:
```
CORS_ORIGINS=https://your-vercel-url.vercel.app,http://localhost:4200
```

OR update `backend/main.py` and redeploy:
```python
allow_origins=[
    "https://your-actual-vercel-url.vercel.app",  # ← Your real Vercel URL
    "http://localhost:4200"
],
```

### 4.3 Redeploy Backend
- In Railway, click "Deploy" again
- Wait 1-2 minutes

---

## 📋 STEP 5: Test Your Deployed App! (2 minutes)

### 5.1 Visit Your Frontend
Open: `https://your-vercel-url.vercel.app`

### 5.2 Test Features
1. **Dashboard:**
   - Click "Load Dashboard"
   - Should show: 0 initially
   - Should load data after clicking

2. **SMS Detection:**
   - Go to "Scan Message"
   - Enter: "URGENT: Click here now!"
   - Click "Scan Now"
   - Should show: SPAM result

3. **Model Performance:**
   - Go to "Performance"
   - Should show: Model metrics (95% accuracy)

---

## 🔧 Troubleshooting

### ❌ "Backend API is not available"

**Solution:**
1. Check Railway backend is running
2. Check backend URL in `environment.prod.ts` is correct
3. Check CORS settings include your Vercel URL
4. Redeploy frontend after fixing

**Test backend directly:**
```
https://your-backend-url.railway.app/api/health
```

### ❌ "CORS Error"

**Solution:**
1. Add your Vercel URL to CORS in `backend/main.py`
2. Redeploy backend on Railway
3. Clear browser cache
4. Test again

### ❌ "Model not loaded"

**Solution:**
The model files are too large for deployment. You have two options:

**Option A: Use smaller model (Recommended)**
Comment out model loading in `backend/main.py`:
```python
@app.on_event("startup")
async def startup_event():
    global predictor
    # Temporarily disable for deployment
    predictor = None
    print("[INFO] Running in demo mode without ML model")
```

**Option B: Upload model to cloud storage**
- Upload model to S3/Google Cloud Storage
- Download on startup in backend

### ❌ Build fails on Vercel

**Check:**
1. Root directory is set to `cybersentinel-dashboard`
2. Build command is correct
3. Output directory is `dist/cybersentinel-dashboard/browser`
4. Node version is 18 or higher

---

## 📊 Expected Results

After successful deployment:

✅ **Backend URL:** `https://xxx.railway.app`
- `/api/health` → Returns healthy status
- `/api/system/status` → Returns system info

✅ **Frontend URL:** `https://xxx.vercel.app`
- Dashboard loads
- SMS Detection works
- Model Performance shows metrics

---

## 🎯 Quick Checklist

- [ ] Railway account created
- [ ] Backend deployed to Railway
- [ ] Backend URL copied
- [ ] `environment.prod.ts` updated with backend URL
- [ ] `backend/main.py` CORS updated
- [ ] Vercel account created
- [ ] Frontend deployed to Vercel
- [ ] Frontend URL copied
- [ ] CORS updated with Vercel URL
- [ ] Backend redeployed
- [ ] Tested all features

---

## 🆘 Still Having Issues?

### Option 1: Use Render (Alternative to Railway)

**Deploy Backend to Render:**
1. Go to **https://render.com**
2. New → Web Service
3. Connect GitHub repo
4. Settings:
   - Build: `pip install -r requirements.txt && pip install -r api_requirements.txt`
   - Start: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Deploy

### Option 2: Deploy Frontend to Netlify (Alternative to Vercel)

**Deploy to Netlify:**
1. Go to **https://netlify.com**
2. New site from Git
3. Select repo
4. Settings:
   - Base: `cybersentinel-dashboard`
   - Build: `npm install && npm run build`
   - Publish: `dist/cybersentinel-dashboard/browser`
5. Deploy

---

## 📞 Support

If deployment still fails:
1. Check Railway logs for backend errors
2. Check Vercel logs for frontend errors
3. Test backend URL directly in browser
4. Check browser console for errors

---

## ✅ Success Criteria

When everything works:

✅ Backend responds at Railway URL
✅ Frontend loads at Vercel URL
✅ Dashboard can load data
✅ SMS Detection can analyze messages
✅ No CORS errors in browser console
✅ All pages navigate properly

---

**Time Required:** 10-15 minutes total
**Cost:** $0 (Both platforms have free tiers)
**Difficulty:** Beginner-friendly

---

## 🎉 Once Deployed

**Share Your URLs:**
- Frontend: `https://your-app.vercel.app`
- Backend: `https://your-api.railway.app`

**Next Steps:**
- Add custom domain (optional)
- Set up monitoring
- Enable analytics
- Add authentication (if needed)

---

**LET'S DEPLOY! Follow steps 1-5 above.** 🚀
