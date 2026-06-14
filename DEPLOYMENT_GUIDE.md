# AI Football Predictor - Deployment Guide

## 📱 Part 1: Deploy the Backend (Render.com - FREE)

### Step 1: Push your code to GitHub
1. Create a GitHub repository
2. Push your entire project folder to GitHub

### Step 2: Deploy to Render
1. Go to https://render.com/ and sign up
2. Click "New +" → "Web Service"
3. Connect your GitHub account and select your repository
4. Configure:
   - Name: `ai-football-prediction-backend`
   - Root Directory: `backend`
   - Runtime: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
   - Plan: Free
5. Add Environment Variable:
   - Key: `FOOTBALL_DATA_API_KEY`
   - Value: Your Football-Data.org API key (9b8474d0031d4a68881e784f2f54d4c3)
6. Click "Deploy Web Service"

### Step 3: Get your backend URL
Once deployed, Render will give you a URL like `https://ai-football-prediction-backend.onrender.com`

---

## 📱 Part 2: Update the App & Build APK

### Step 1: Update API URL
1. Open `frontend-web/index.html`
2. Change line 316 from:
   ```javascript
   const API_URL = '/api';
   ```
   to your Render URL:
   ```javascript
   const API_URL = 'https://ai-football-prediction-backend.onrender.com/api';
   ```

### Step 2: Sync web assets to Android
```bash
npx cap sync android
```

### Step 3: Build the APK
You need Android Studio to build the APK:
1. Download and install Android Studio: https://developer.android.com/studio
2. Open the `android` folder in Android Studio
3. Wait for Gradle sync to complete
4. Click "Build" → "Build Bundle(s) / APK(s)" → "Build APK(s)"
5. Once built, find your APK in: `android/app/build/outputs/apk/debug/app-debug.apk`

---

## 📱 Quick Test (Without Deploying Backend)
If you just want to test the APK locally:
1. Keep your Flask server running (`python app.py`)
2. Find your computer's local IP address
3. Update `API_URL` in `index.html` to `http://YOUR_LOCAL_IP:5000/api`
4. Build APK as above

Note: This will only work on your local Wi-Fi network
