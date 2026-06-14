
# AI Football Match Prediction App

A fully-featured AI-powered football match prediction application with a Python Flask backend and both web & Flutter frontends!

## ✅ APP IS READY TO USE!
Your app is live at: **http://localhost:5000**

Just open that URL in your browser!

## Features

### 🐍 Backend (Python Flask)
- **Real Data Integration**: Football-Data.org API for live and historical match data
- **AI Prediction Model**: Gradient Boosting classifier for match outcome predictions
- **13 Supported Competitions**:
  - Premier League (England)
  - Championship (England)
  - La Liga (Spain)
  - Serie A (Italy)
  - Bundesliga (Germany)
  - Ligue 1 (France)
  - Eredivisie (Netherlands)
  - Primeira Liga (Portugal)
  - Campeonato Brasileiro Série A (Brazil)
  - UEFA Champions League
  - Copa Libertadores
  - European Championship
  - FIFA World Cup
- **RESTful API**:
  - `/api/competitions` - List all competitions
  - `/api/upcoming-matches` - Get upcoming matches (filter by competition)
  - `/api/live-matches` - Get live matches
  - `/api/standings/<competition_id>` - Get league standings
  - `/api/predict/<match_id>` - Get AI prediction for match
  - `/api/predict-direct` - Direct prediction from team names

### 🌐 Frontend (Web Browser - Works NOW!)
- Beautiful Material Design-inspired interface
- Competition selector dropdown
- Upcoming matches view
- Live matches view
- Standings view with league tables
- Match prediction screen with animated probability bars
- Responsive design for all screen sizes
- No installation needed - just use your browser!

### 📱 Frontend (Flutter)
- Material Design 3 UI
- Competition selector dropdown
- Upcoming matches view
- Live matches view
- Standings view with table
- Match prediction screen with probability bars
- Beautiful and responsive interface

## Project Structure

```
AI Football match Prediction/
├── backend/
│   ├── app.py                    # Main Flask application
│   ├── enhanced_prediction_model.py # AI prediction model
│   ├── requirements.txt          # Python dependencies
│   ├── .env                      # Your API key (already configured)
│   ├── .env.example              # Example environment config
│   └── prediction_model.py       # Original prediction model (legacy)
├── frontend/
│   ├── lib/
│   │   └── main.dart             # Flutter app main file
│   ├── pubspec.yaml              # Flutter dependencies
│   ├── analysis_options.yaml
│   ├── .gitignore
│   └── setup.bat                 # Windows setup script
└── README.md
```

## Backend Setup (Already Done!)

Your backend is already running! If you ever need to restart it:

```bash
cd backend
pip install -r requirements.txt
python app.py
```

## Flutter Frontend Setup

### Step 1: Install Flutter
Download and install Flutter from: https://flutter.dev/docs/get-started/install

### Step 2: Initialize the Flutter Project
Open a terminal in the `frontend` directory and run:
```bash
flutter create .
flutter pub get
```
Or double-click `setup.bat` in the frontend directory (Windows only)

### Step 3: Run the App
Connect your Android device via USB (enable USB debugging in developer options), or start an emulator, then run:
```bash
flutter run
```

## Using the API

### Get Competitions List
```bash
curl http://localhost:5000/api/competitions
```

### Get Upcoming Matches
```bash
curl http://localhost:5000/api/upcoming-matches
# Or for specific competition:
curl http://localhost:5000/api/upcoming-matches?competition_id=2021
```

### Get Standings
```bash
curl http://localhost:5000/api/standings/2021
```

### Predict Match Outcome
```bash
curl http://localhost:5000/api/predict/<match_id>
```

## Improving the AI Model

The current prediction model can be enhanced by:
1. Training on more historical data (uncomment `predictor.initialize_all_models()`)
2. Adding more features (head-to-head records, recent form, injuries, etc.)
3. Hyperparameter tuning
4. Adding more sophisticated models (neural networks, ensemble methods)

## Notes

- You need a valid Football-Data.org API key (already set up in your .env)
- Free API tier has some rate limits and access restrictions
- Consider upgrading to a paid plan for more leagues and more historical data
