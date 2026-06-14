
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import joblib
import os

def create_sample_data():
    data = {
        'home_team': ['Team A', 'Team B', 'Team C', 'Team A', 'Team D', 'Team B'],
        'away_team': ['Team B', 'Team A', 'Team D', 'Team C', 'Team C', 'Team D'],
        'home_goals': [2, 1, 3, 0, 2, 1],
        'away_goals': [1, 2, 1, 2, 2, 0],
        'result': ['home_win', 'away_win', 'home_win', 'away_win', 'draw', 'home_win']
    }
    return pd.DataFrame(data)

class FootballPredictor:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.home_encoder = LabelEncoder()
        self.away_encoder = LabelEncoder()
        self.is_trained = False
        
    def train(self, df):
        df_encoded = df.copy()
        df_encoded['home_team_encoded'] = self.home_encoder.fit_transform(df_encoded['home_team'])
        df_encoded['away_team_encoded'] = self.away_encoder.fit_transform(df_encoded['away_team'])
        
        X = df_encoded[['home_team_encoded', 'away_team_encoded']]
        y = df_encoded['result']
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        self.model.fit(X_train, y_train)
        self.is_trained = True
        
        print(f"Model trained. Accuracy: {self.model.score(X_test, y_test):.2f}")
        
    def predict(self, home_team, away_team):
        if not self.is_trained:
            return {'home_win_prob': 0.45, 'draw_prob': 0.30, 'away_win_prob': 0.25, 'predicted_winner': home_team}
        
        try:
            home_encoded = self.home_encoder.transform([home_team])[0]
            away_encoded = self.away_encoder.transform([away_team])[0]
        except ValueError:
            return {'home_win_prob': 0.45, 'draw_prob': 0.30, 'away_win_prob': 0.25, 'predicted_winner': home_team}
        
        X = np.array([[home_encoded, away_encoded]])
        prediction = self.model.predict(X)[0]
        probabilities = self.model.predict_proba(X)[0]
        
        result_probs = dict(zip(self.model.classes_, probabilities))
        
        home_win_prob = result_probs.get('home_win', 0.33)
        draw_prob = result_probs.get('draw', 0.33)
        away_win_prob = result_probs.get('away_win', 0.33)
        
        if prediction == 'home_win':
            predicted_winner = home_team
        elif prediction == 'away_win':
            predicted_winner = away_team
        else:
            predicted_winner = 'Draw'
            
        return {
            'home_win_prob': float(home_win_prob),
            'draw_prob': float(draw_prob),
            'away_win_prob': float(away_win_prob),
            'predicted_winner': predicted_winner
        }

predictor = FootballPredictor()
sample_data = create_sample_data()
predictor.train(sample_data)
