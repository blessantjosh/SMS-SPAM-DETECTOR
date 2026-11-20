# 🚀 CyberSentinel AI - Deployment Guide

## 📦 GitHub Repository

**Repository:** https://github.com/blessantjosh/SMS-SPAM-DETECTOR

✅ **Successfully pushed to GitHub!**

---

## 🎯 Deployment Options

### Option 1: Vercel (Recommended for Frontend + API Routes)

#### **Frontend Deployment:**

1. **Connect to GitHub:**
   - Go to [vercel.com](https://vercel.com)
   - Click "Import Project"
   - Select your GitHub repository: `blessantjosh/SMS-SPAM-DETECTOR`

2. **Configure Build Settings:**
   ```
   Framework Preset: Angular
   Build Command: cd cybersentinel-dashboard && npm install && npm run build
   Output Directory: cybersentinel-dashboard/dist/cybersentinel-dashboard/browser
   Install Command: npm install
   ```

3. **Environment Variables:**
   ```
   API_URL=https://your-backend-url.com/api
   ```

4. **Deploy:**
   - Click "Deploy"
   - Wait for build to complete
   - Get deployment URL: `https://cybersentinel-ai.vercel.app`

#### **Backend Deployment (Vercel Serverless):**

Create `vercel.json` in project root:
```json
{
  "version": 2,
  "builds": [
    {
      "src": "backend/main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "backend/main.py"
    }
  ]
}
```

---

### Option 2: Railway (Full Stack - Backend + Frontend)

#### **Backend Deployment:**

1. **Go to [railway.app](https://railway.app)**
2. **New Project → Deploy from GitHub**
3. **Select repository:** `SMS-SPAM-DETECTOR`
4. **Configure:**
   ```
   Start Command: cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
   Build Command: pip install -r requirements.txt && pip install -r api_requirements.txt
   ```
5. **Add Environment Variables:**
   ```
   PORT=8000
   PYTHONPATH=/app/src
   ```
6. **Get backend URL:** `https://cybersentinel-api.railway.app`

#### **Frontend Deployment:**

1. **New Service → Deploy from GitHub**
2. **Select same repository**
3. **Configure:**
   ```
   Root Directory: cybersentinel-dashboard
   Build Command: npm install && npm run build
   Start Command: npm run start
   ```
4. **Environment Variables:**
   ```
   API_URL=https://cybersentinel-api.railway.app/api
   ```

---

### Option 3: Render (Free Tier Available)

#### **Backend (Web Service):**

1. **Go to [render.com](https://render.com)**
2. **New → Web Service**
3. **Connect GitHub repository**
4. **Configure:**
   ```
   Name: cybersentinel-backend
   Environment: Python 3
   Build Command: pip install -r requirements.txt && pip install -r api_requirements.txt
   Start Command: cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
   ```
5. **Environment Variables:**
   ```
   PYTHONPATH=/opt/render/project/src
   ```

#### **Frontend (Static Site):**

1. **New → Static Site**
2. **Connect same repository**
3. **Configure:**
   ```
   Build Command: cd cybersentinel-dashboard && npm install && npm run build
   Publish Directory: cybersentinel-dashboard/dist/cybersentinel-dashboard/browser
   ```

---

### Option 4: Netlify (Frontend Only)

1. **Go to [netlify.com](https://netlify.com)**
2. **Import from Git → Select repository**
3. **Configure:**
   ```
   Base Directory: cybersentinel-dashboard
   Build Command: npm install && npm run build
   Publish Directory: dist/cybersentinel-dashboard/browser
   ```
4. **Environment Variables:**
   ```
   API_URL=your-backend-url
   ```

---

### Option 5: Heroku

#### **Backend:**

Create `Procfile`:
```
web: cd backend && uvicorn main:app --host=0.0.0.0 --port=$PORT
```

Create `runtime.txt`:
```
python-3.10.12
```

Deploy:
```bash
heroku create cybersentinel-backend
git push heroku main
```

#### **Frontend:**

Deploy to Heroku or use Netlify/Vercel for frontend.

---

### Option 6: AWS (Production Grade)

#### **Backend (Elastic Beanstalk or Lambda):**

1. **Elastic Beanstalk:**
   - Package backend as Python application
   - Deploy using EB CLI
   - Configure environment variables

2. **Lambda + API Gateway:**
   - Use AWS SAM or Serverless Framework
   - Deploy FastAPI as Lambda function

#### **Frontend (S3 + CloudFront):**

1. Build frontend: `npm run build`
2. Upload to S3 bucket
3. Configure CloudFront distribution
4. Set up custom domain

---

### Option 7: Azure

#### **Backend (App Service):**

1. Create App Service (Python)
2. Deploy via GitHub Actions
3. Configure startup command

#### **Frontend (Static Web Apps):**

1. Create Static Web App
2. Connect to GitHub
3. Configure build

---

### Option 8: Google Cloud Platform

#### **Backend (Cloud Run):**

Create `Dockerfile`:
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt api_requirements.txt ./
RUN pip install -r requirements.txt && pip install -r api_requirements.txt

COPY . .

ENV PYTHONPATH=/app/src

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

Deploy:
```bash
gcloud run deploy cybersentinel-backend \
  --source . \
  --platform managed \
  --region us-central1
```

#### **Frontend (Firebase Hosting):**

```bash
firebase init hosting
firebase deploy
```

---

## 🔧 Environment Configuration

### Backend Environment Variables:

```env
# API Configuration
PORT=8000
HOST=0.0.0.0

# Model Configuration
MODEL_PATH=./models/trained
MODEL_NAME=logistic_regression

# CORS Origins
CORS_ORIGINS=https://your-frontend-url.com,http://localhost:4200

# Python Path
PYTHONPATH=./src
```

### Frontend Environment Variables:

Create `cybersentinel-dashboard/src/environments/environment.prod.ts`:
```typescript
export const environment = {
  production: true,
  apiUrl: 'https://your-backend-url.com/api'
};
```

Update `api.service.ts`:
```typescript
import { environment } from '../environments/environment';

private baseUrl = environment.apiUrl;
```

---

## 📊 GitHub Actions (Already Set Up)

The repository includes GitHub Actions workflow (`.github/workflows/deploy.yml`) that:

✅ Runs on every push to main
✅ Sets up Python and Node.js
✅ Installs dependencies
✅ Builds frontend
✅ Runs tests
✅ Creates deployment artifacts

**To enable:**
1. Go to GitHub → Settings → Actions
2. Enable workflows
3. Push to main branch

---

## 🔐 Security Checklist

Before deploying to production:

- [ ] Add `.env` files to `.gitignore`
- [ ] Use environment variables for sensitive data
- [ ] Enable HTTPS/SSL
- [ ] Configure CORS properly
- [ ] Set up rate limiting
- [ ] Add authentication if needed
- [ ] Enable API key protection
- [ ] Set up monitoring and logging
- [ ] Configure backup strategy
- [ ] Add error tracking (Sentry)

---

## 📈 Performance Optimization

### Backend:
- [ ] Use gunicorn with multiple workers
- [ ] Enable caching for predictions
- [ ] Add Redis for session management
- [ ] Use CDN for static files
- [ ] Enable compression

### Frontend:
- [ ] Enable Angular production mode
- [ ] Use lazy loading for routes
- [ ] Enable service workers
- [ ] Compress images
- [ ] Minify CSS/JS

---

## 🧪 Testing Deployment

### Test Backend:
```bash
curl https://your-backend-url.com/api/health
curl https://your-backend-url.com/api/system/status
```

### Test Frontend:
1. Open: `https://your-frontend-url.com`
2. Check dashboard loads
3. Test SMS detection
4. Verify model performance page
5. Check all navigation works

---

## 📱 Custom Domain Setup

### Vercel:
1. Go to Project Settings → Domains
2. Add your custom domain
3. Configure DNS records
4. Wait for SSL certificate

### Railway:
1. Settings → Custom Domain
2. Add domain
3. Configure CNAME record

### Netlify:
1. Domain Settings → Add custom domain
2. Configure DNS
3. Enable HTTPS

---

## 🔄 Continuous Deployment

**Automatic deployment is set up!**

Every time you push to GitHub:
1. GitHub Actions runs
2. Tests execute
3. Build completes
4. Deployment triggers

To deploy updates:
```bash
git add .
git commit -m "Update: Your changes"
git push origin main
```

---

## 📊 Monitoring

### Recommended Tools:

1. **Uptime Monitoring:**
   - UptimeRobot (free)
   - Pingdom
   - StatusCake

2. **Error Tracking:**
   - Sentry
   - Rollbar
   - Bugsnag

3. **Analytics:**
   - Google Analytics
   - Plausible
   - Mixpanel

4. **Performance:**
   - Lighthouse
   - WebPageTest
   - GTmetrix

---

## 🆘 Troubleshooting

### Build Fails:
- Check Node.js version (use 18+)
- Verify Python version (use 3.10+)
- Check dependency versions

### Backend 502 Error:
- Check start command
- Verify PORT environment variable
- Check PYTHONPATH configuration

### Frontend API Errors:
- Update API_URL in environment
- Check CORS configuration
- Verify backend is running

### Model Loading Error:
- Ensure models directory is included
- Check model file path
- Verify PYTHONPATH

---

## ✅ Quick Deploy Commands

### Update and Push:
```bash
git add .
git commit -m "Update: Your message"
git push origin main
```

### Manual Backend Deploy (Railway):
```bash
railway up
```

### Manual Frontend Build:
```bash
cd cybersentinel-dashboard
npm run build
```

---

## 🎯 Recommended Setup (Easiest)

**For Quick Deployment:**

1. **Frontend:** Vercel (Free, automatic deployment)
2. **Backend:** Railway (Free tier, easy setup)
3. **Total Time:** 10-15 minutes

**Steps:**
1. ✅ Push to GitHub (Already done!)
2. Connect Vercel to repository (Frontend)
3. Connect Railway to repository (Backend)
4. Update frontend API URL
5. Done! 🎉

---

## 📞 Need Help?

**Repository:** https://github.com/blessantjosh/SMS-SPAM-DETECTOR

**Issues:** https://github.com/blessantjosh/SMS-SPAM-DETECTOR/issues

---

## 🎉 Success Metrics

Once deployed, you should have:

✅ Frontend accessible at custom URL
✅ Backend API responding
✅ SMS detection working
✅ Dashboard loading stats
✅ Model performance displaying
✅ Automatic deployments on push
✅ SSL/HTTPS enabled
✅ Monitoring active

---

**Deployed:** Ready to deploy!
**Status:** ✅ Code pushed to GitHub
**Next Step:** Choose deployment platform and deploy!
