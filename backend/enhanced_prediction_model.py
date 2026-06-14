
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import requests
import os
import pickle
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

API_KEY = os.getenv('FOOTBALL_DATA_API_KEY')
BASE_URL = 'https://api.football-data.org/v4'
headers = {'X-Auth-Token': API_KEY}

AVAILABLE_COMPETITIONS = [
    {'id': 2013, 'name': 'Campeonato Brasileiro Série A', 'code': 'BSA'},
    {'id': 2016, 'name': 'Championship', 'code': 'ELC'},
    {'id': 2021, 'name': 'Premier League', 'code': 'PL'},
    {'id': 2001, 'name': 'UEFA Champions League', 'code': 'CL'},
    {'id': 2018, 'name': 'European Championship', 'code': 'EC'},
    {'id': 2015, 'name': 'Ligue 1', 'code': 'FL1'},
    {'id': 2002, 'name': 'Bundesliga', 'code': 'BL1'},
    {'id': 2019, 'name': 'Serie A', 'code': 'SA'},
    {'id': 2003, 'name': 'Eredivisie', 'code': 'DED'},
    {'id': 2017, 'name': 'Primeira Liga', 'code': 'PPL'},
    {'id': 2152, 'name': 'Copa Libertadores', 'code': 'CLI'},
    {'id': 2014, 'name': 'Primera Division', 'code': 'PD'},
    {'id': 2000, 'name': 'FIFA World Cup', 'code': 'WC'},
]

MODELS_DIR = os.path.join(os.path.dirname(__file__), 'models')
if not os.path.exists(MODELS_DIR):
    os.makedirs(MODELS_DIR)

class EnhancedFootballPredictor:
    def __init__(self):
        self.models = {}
        self.team_encoders = {}
        self.team_stats = {}
        self.h2h_records = {}
        self.team_elo = {}
        self.is_trained = False
        self.load_models()
        
    def save_models(self):
        """Save trained models and encoders to disk"""
        try:
            data = {
                'models': self.models,
                'team_encoders': self.team_encoders,
                'team_stats': self.team_stats,
                'h2h_records': self.h2h_records,
                'is_trained': self.is_trained
            }
            with open(os.path.join(MODELS_DIR, 'predictor_data.pkl'), 'wb') as f:
                pickle.dump(data, f)
            print("💾 Models and data saved to disk!")
        except Exception as e:
            print(f"❌ Error saving models: {e}")

    def load_models(self):
        """Load models and data from disk if available"""
        filepath = os.path.join(MODELS_DIR, 'predictor_data.pkl')
        if os.path.exists(filepath):
            try:
                with open(filepath, 'rb') as f:
                    data = pickle.load(f)
                    self.models = data.get('models', {})
                    self.team_encoders = data.get('team_encoders', {})
                    self.team_stats = data.get('team_stats', {})
                    self.h2h_records = data.get('h2h_records', {})
                    self.is_trained = data.get('is_trained', False)
                print("📂 Models and data loaded from disk!")
            except Exception as e:
                print(f"⚠️  Error loading models: {e}")
        else:
            print("ℹ️  No saved models found. Ready for training.")

    def fetch_historical_matches(self, competition_id, days_back=365):
        matches = []
        date_to = datetime.now().strftime('%Y-%m-%d')
        date_from = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        
        try:
            url = f"{BASE_URL}/competitions/{competition_id}/matches"
            params = {'dateFrom': date_from, 'dateTo': date_to}
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                for match in data.get('matches', []):
                    if match['status'] == 'FINISHED':
                        home_goals = match['score']['fullTime'].get('home', 0)
                        away_goals = match['score']['fullTime'].get('away', 0)
                        
                        if home_goals is None or away_goals is None:
                            continue
                            
                        matches.append({
                            'home_team': match['homeTeam']['name'],
                            'away_team': match['awayTeam']['name'],
                            'home_goals': int(home_goals),
                            'away_goals': int(away_goals),
                            'result': self._determine_result(match)
                        })
        except Exception as e:
            print(f"Error fetching data for {competition_id}: {e}")
            
        return matches
    
    def _determine_result(self, match):
        home_goals = match['score']['fullTime'].get('home', 0)
        away_goals = match['score']['fullTime'].get('away', 0)
        
        if home_goals > away_goals:
            return 'home_win'
        elif home_goals < away_goals:
            return 'away_win'
        else:
            return 'draw'
    
    def compute_team_stats(self, matches):
        stats = {}
        h2h = {}
        
        for match in matches:
            home = match['home_team']
            away = match['away_team']
            
            if home not in stats:
                stats[home] = {'goals_for': 0, 'goals_against': 0, 'wins': 0, 'draws': 0, 'losses': 0, 'matches': 0, 'recent_form': []}
            if away not in stats:
                stats[away] = {'goals_for': 0, 'goals_against': 0, 'wins': 0, 'draws': 0, 'losses': 0, 'matches': 0, 'recent_form': []}
            
            key = tuple(sorted([home, away]))
            if key not in h2h:
                h2h[key] = {'home_wins': 0, 'away_wins': 0, 'draws': 0}
            
            if match['result'] == 'home_win':
                h2h[key]['home_wins'] += 1
                stats[home]['recent_form'].append(3)
                stats[away]['recent_form'].append(0)
            elif match['result'] == 'away_win':
                h2h[key]['away_wins'] += 1
                stats[home]['recent_form'].append(0)
                stats[away]['recent_form'].append(3)
            else:
                h2h[key]['draws'] += 1
                stats[home]['recent_form'].append(1)
                stats[away]['recent_form'].append(1)
            
            stats[home]['goals_for'] += match['home_goals']
            stats[home]['goals_against'] += match['away_goals']
            stats[home]['matches'] += 1
            if match['result'] == 'home_win':
                stats[home]['wins'] +=1
            elif match['result'] == 'draw':
                stats[home]['draws'] +=1
            else:
                stats[home]['losses'] +=1
                
            stats[away]['goals_for'] += match['away_goals']
            stats[away]['goals_against'] += match['home_goals']
            stats[away]['matches'] +=1
            if match['result'] == 'away_win':
                stats[away]['wins'] +=1
            elif match['result'] == 'draw':
                stats[away]['draws'] +=1
            else:
                stats[away]['losses'] +=1
                
        for team in stats:
            if stats[team]['matches'] > 0:
                stats[team]['avg_goals_for'] = stats[team]['goals_for'] / stats[team]['matches']
                stats[team]['avg_goals_against'] = stats[team]['goals_against'] / stats[team]['matches']
                stats[team]['win_rate'] = stats[team]['wins'] / stats[team]['matches']
                stats[team]['strength'] = (stats[team]['avg_goals_for'] + 0.3) / (stats[team]['avg_goals_against'] + 0.3)
                
                recent = stats[team]['recent_form'][-6:] if len(stats[team]['recent_form']) >= 6 else stats[team]['recent_form']
                stats[team]['recent_form_score'] = sum(recent) / len(recent) if recent else 1.5
            else:
                stats[team]['avg_goals_for'] = 1.3
                stats[team]['avg_goals_against'] = 1.3
                stats[team]['win_rate'] = 0.33
                stats[team]['strength'] = 1.0
                stats[team]['recent_form_score'] = 1.5
                
        return stats, h2h
    
    def train_competition_model(self, competition_id):
        print(f"🎯 Training model for competition {competition_id}...")
        matches = self.fetch_historical_matches(competition_id, days_back=365)
        
        if len(matches) < 10:
            print(f"⚠️  Not enough historical data for {competition_id}")
            return False
            
        df = pd.DataFrame(matches)
        self.team_stats[competition_id], self.h2h_records[competition_id] = self.compute_team_stats(matches)
        
        all_teams = pd.concat([df['home_team'], df['away_team']]).unique()
        all_teams = np.append(all_teams, 'Unknown')
        team_encoder = LabelEncoder()
        team_encoder.fit(all_teams)
        
        X = []
        y = []
        
        for _, row in df.iterrows():
            home = row['home_team']
            away = row['away_team']
            
            home_stats = self.team_stats[competition_id].get(home, {'avg_goals_for': 1.3, 'avg_goals_against': 1.3, 'win_rate': 0.33, 'strength': 1.0, 'recent_form_score': 1.5})
            away_stats = self.team_stats[competition_id].get(away, {'avg_goals_for': 1.3, 'avg_goals_against': 1.3, 'win_rate': 0.33, 'strength': 1.0, 'recent_form_score': 1.5})
            
            X.append([
                team_encoder.transform([home])[0],
                team_encoder.transform([away])[0],
                home_stats['avg_goals_for'],
                home_stats['avg_goals_against'],
                home_stats['win_rate'],
                home_stats['strength'],
                home_stats['recent_form_score'],
                away_stats['avg_goals_for'],
                away_stats['avg_goals_against'],
                away_stats['win_rate'],
                away_stats['strength'],
                away_stats['recent_form_score'],
                1.0
            ])
            y.append(row['result'])
            
        model = RandomForestClassifier(n_estimators=400, max_depth=8, random_state=42, min_samples_split=5)
        model.fit(X, y)
            
        self.models[competition_id] = model
        self.team_encoders[competition_id] = team_encoder
        print(f"✅ Model trained for {competition_id}! Matches used: {len(matches)}")
        self.save_models()
        return True
    
    def predict_match(self, home_team, away_team, competition_id=None):
        if not competition_id or competition_id not in self.models:
            return self._ultra_smart_prediction(home_team, away_team)
            
        try:
            team_encoder = self.team_encoders[competition_id]
            
            # Safe transform for teams
            home_encoded = team_encoder.transform([home_team])[0] if home_team in team_encoder.classes_ else team_encoder.transform(['Unknown'])[0]
            away_encoded = team_encoder.transform([away_team])[0] if away_team in team_encoder.classes_ else team_encoder.transform(['Unknown'])[0]
            
            home_stats = self.team_stats[competition_id].get(home_team, {'avg_goals_for': 1.3, 'avg_goals_against': 1.3, 'win_rate': 0.33, 'strength': 1.0, 'recent_form_score': 1.5})
            away_stats = self.team_stats[competition_id].get(away_team, {'avg_goals_for': 1.3, 'avg_goals_against': 1.3, 'win_rate': 0.33, 'strength': 1.0, 'recent_form_score': 1.5})
            
            features = np.array([[
                home_encoded,
                away_encoded,
                home_stats['avg_goals_for'],
                home_stats['avg_goals_against'],
                home_stats['win_rate'],
                home_stats['strength'],
                home_stats['recent_form_score'],
                away_stats['avg_goals_for'],
                away_stats['avg_goals_against'],
                away_stats['win_rate'],
                away_stats['strength'],
                away_stats['recent_form_score'],
                1.0
            ]])
            
            result = self.models[competition_id].predict(features)[0]
            proba = self.models[competition_id].predict_proba(features)[0]
            class_probs = dict(zip(self.models[competition_id].classes_, proba))
            
            home_win = class_probs.get('home_win', 0.43)
            draw = class_probs.get('draw', 0.27)
            away_win = class_probs.get('away_win', 0.30)
            
        except Exception as e:
            print(f"⚠️  Model prediction failed: {e}, using ultra smart fallback")
            return self._ultra_smart_prediction(home_team, away_team)
            
        if result == 'home_win':
            predicted_winner = home_team
        elif result == 'away_win':
            predicted_winner = away_team
        else:
            predicted_winner = 'Draw'
            
        return {
            'home_win_prob': float(home_win),
            'draw_prob': float(draw),
            'away_win_prob': float(away_win),
            'predicted_winner': predicted_winner
        }
    
    def _ultra_smart_prediction(self, home_team, away_team):
        home_win = 0.46
        draw = 0.28
        away_win = 0.26
        
        elite_tiers = [
            'Brazil', 'Germany', 'France', 'Spain', 'Argentina', 'England', 'Italy',
            'Manchester City', 'Liverpool', 'Arsenal', 'Chelsea', 'Barcelona', 'Real Madrid',
            'Bayern Munich', 'Juventus', 'Paris Saint-Germain', 'Atletico Madrid', 'Inter Milan', 'AC Milan',
            'Napoli', 'Manchester United', 'Tottenham', 'Newcastle', 'Borussia Dortmund', 'RB Leipzig',
            'Bayer Leverkusen', 'Lyon', 'Marseille', 'Sevilla', 'Valencia', 'AS Roma', 'Lazio'
        ]
        
        top_tiers = [
            'Portugal', 'Netherlands', 'Belgium', 'Uruguay', 'Croatia', 'Denmark',
            'Portugal', 'Switzerland', 'Mexico', 'USA', 'Japan', 'South Korea',
            'Aston Villa', 'Brighton', 'West Ham', 'Chelsea', 'Fulham',
            'Real Sociedad', 'Villarreal', 'Atalanta', 'Fiorentina',
            'Bayer Leverkusen', 'Union Berlin', 'Eintracht Frankfurt',
            'Nice', 'Monaco', 'Lille'
        ]
        
        mid_tiers = [
            'Scotland', 'Wales', 'Poland', 'Sweden', 'Serbia',
            'Wolverhampton', 'Crystal Palace', 'Nottingham Forest',
            'Getafe', 'Osasuna', 'Celta Vigo', 'Udinese', 'Sassuolo',
            'Mainz', 'Cologne', 'Freiburg', 'Montpellier', 'Reims', 'Lens'
        ]
        
        home_score = 0
        away_score = 0
        
        for team in elite_tiers:
            if team.lower() in home_team.lower():
                home_score += 5
            if team.lower() in away_team.lower():
                away_score +=5
                
        for team in top_tiers:
            if team.lower() in home_team.lower():
                home_score += 3
            if team.lower() in away_team.lower():
                away_score +=3
                
        for team in mid_tiers:
            if team.lower() in home_team.lower():
                home_score += 1.5
            if team.lower() in away_team.lower():
                away_score +=1.5
                
        diff = home_score - away_score
        
        if diff > 4:
            home_win = 0.72
            away_win = 0.14
        elif diff > 2:
            home_win = 0.60
            away_win = 0.20
        elif diff > 0:
            home_win = 0.52
            away_win = 0.25
        elif diff < -4:
            away_win = 0.68
            home_win = 0.16
        elif diff < -2:
            away_win = 0.58
            home_win = 0.22
        elif diff < 0:
            away_win = 0.50
            home_win = 0.30
            
        total = home_win + draw + away_win
        home_win /= total
        draw /= total
        away_win /= total
        
        if home_win > away_win and home_win > draw:
            predicted = home_team
        elif away_win > home_win and away_win > draw:
            predicted = away_team
        else:
            predicted = 'Draw'
            
        return {
            'home_win_prob': float(home_win),
            'draw_prob': float(draw),
            'away_win_prob': float(away_win),
            'predicted_winner': predicted
        }
    
    def initialize_all_models(self):
        print("🚀 Initializing AI prediction models with historical data...")
        trained = 0
        for comp in AVAILABLE_COMPETITIONS:
            if self.train_competition_model(comp['id']):
                trained += 1
        self.is_trained = True
        print(f"✅ Initialized {trained} advanced models!")
        return True

predictor = EnhancedFootballPredictor()

try:
    print("🏆 Starting ULTRA ACCURATE AI prediction system...")
except Exception as e:
    print(f"⚠️  Initialization note: {e}")
