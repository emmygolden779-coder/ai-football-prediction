
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv
from enhanced_prediction_model import predictor, AVAILABLE_COMPETITIONS

load_dotenv()

app = Flask(__name__, static_folder='../frontend-web', static_url_path='')
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

FOOTBALL_DATA_API_KEY = os.getenv('FOOTBALL_DATA_API_KEY')
BASE_URL = 'https://api.football-data.org/v4'

headers = {'X-Auth-Token': FOOTBALL_DATA_API_KEY}

# Initialize the models on app startup
print("🚀 Initializing ULTRA ACCURATE AI prediction system...")
try:
    if not predictor.is_trained:
        print("📊 No trained models found. Starting initialization (this may take a minute)...")
        # Run initialization in a separate thread to not block app startup if needed, 
        # but for now we'll do it synchronously to ensure models are ready.
        predictor.initialize_all_models()
    else:
        print("✅ Models already trained and loaded!")
    
    predictor._ultra_smart_prediction("Team A", "Team B")
    print("✅ Prediction system ready!")
    print("💡 Using ELITE tier classification and form analysis...")
except Exception as e:
    print(f"⚠️  Initialization note: {e}")

@app.route('/')
def home():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/competitions', methods=['GET'])
def get_competitions():
    """Get list of available competitions"""
    return jsonify({
        'competitions': AVAILABLE_COMPETITIONS
    })

@app.route('/api/upcoming-matches', methods=['GET'])
def get_upcoming_matches():
    """Get upcoming matches, optionally filtered by competition"""
    competition_id = request.args.get('competition_id')
    
    try:
        if competition_id:
            url = f"{BASE_URL}/competitions/{competition_id}/matches?status=SCHEDULED"
        else:
            url = f"{BASE_URL}/matches?status=SCHEDULED"
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/live-matches', methods=['GET'])
def get_live_matches():
    """Get live matches"""
    try:
        url = f"{BASE_URL}/matches?status=LIVE"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/matches/<int:competition_id>', methods=['GET'])
def get_competition_matches(competition_id):
    """Get matches for a specific competition"""
    try:
        url = f"{BASE_URL}/competitions/{competition_id}/matches"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/standings/<int:competition_id>', methods=['GET'])
def get_standings(competition_id):
    """Get standings for a specific competition"""
    try:
        url = f"{BASE_URL}/competitions/{competition_id}/standings"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/predict/<int:match_id>', methods=['GET'])
def predict_match(match_id):
    """Get prediction for a specific match - using home/away from query params"""
    try:
        home_team = request.args.get('homeTeam')
        away_team = request.args.get('awayTeam')
        competition_id = request.args.get('competitionId')
        
        if not home_team or not away_team:
            return jsonify({'error': 'homeTeam and awayTeam required'}), 400
        
        # Get prediction
        prediction_result = predictor.predict_match(home_team, away_team, competition_id)
        
        prediction = {
            'match_id': match_id,
            'home_team': home_team,
            'away_team': away_team,
            'competition_id': competition_id,
            'home_win_prob': prediction_result['home_win_prob'],
            'draw_prob': prediction_result['draw_prob'],
            'away_win_prob': prediction_result['away_win_prob'],
            'predicted_winner': prediction_result['predicted_winner']
        }
        
        return jsonify(prediction)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/predict-direct', methods=['POST'])
def predict_direct():
    """Predict match directly from team names"""
    try:
        data = request.json
        home_team = data.get('home_team')
        away_team = data.get('away_team')
        competition_id = data.get('competition_id')
        
        if not home_team or not away_team:
            return jsonify({'error': 'home_team and away_team are required'}), 400
        
        prediction_result = predictor.predict_match(home_team, away_team, competition_id)
        
        return jsonify({
            'home_team': home_team,
            'away_team': away_team,
            'competition_id': competition_id,
            **prediction_result
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/train-model', methods=['POST'])
def train_model():
    """Train model for a specific competition"""
    try:
        data = request.json
        competition_id = data.get('competition_id')
        if not competition_id:
            return jsonify({'error': 'competition_id required'}), 400
            
        success = predictor.train_competition_model(competition_id)
        if success:
            return jsonify({'status': 'success', 'message': f'Model trained for competition {competition_id}'})
        else:
            return jsonify({'status': 'warning', 'message': 'Not enough historical data'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/train-all-models', methods=['POST'])
def train_all_models():
    """Train all available models"""
    try:
        trained = predictor.initialize_all_models()
        return jsonify({'status': 'success', 'message': 'Models training complete!'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
