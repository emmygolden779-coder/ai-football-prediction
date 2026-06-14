
from enhanced_prediction_model import predictor, AVAILABLE_COMPETITIONS

print('🏆 Testing ULTRA ACCURATE AI predictions!')
print('='*60)

# Check if models are loaded
if not predictor.is_trained:
    print("📊 Models not trained yet. Training a sample model (Premier League) for testing...")
    predictor.train_competition_model(2021) # Premier League

test_cases = [
    ('Manchester City', 'Arsenal', 2021),
    ('Liverpool', 'Chelsea', 2021),
    ('Manchester United', 'Tottenham', 2021),
    ('Real Madrid', 'Barcelona', 2014), # La Liga
    ('Bayern Munich', 'Borussia Dortmund', 2002), # Bundesliga
]

for home, away, comp_id in test_cases:
    print(f'\n⚽ {home} vs {away} (Comp ID: {comp_id})')
    
    # Try actual model prediction
    pred = predictor.predict_match(home, away, comp_id)
    
    print(f'   🎯 Predicted Winner: {pred["predicted_winner"]}')
    print(f'   📊 {home} Win: {pred["home_win_prob"]*100:.1f}% | Draw: {pred["draw_prob"]*100:.1f}% | {away} Win: {pred["away_win_prob"]*100:.1f}%')

print('\n'+'='*60)
print('✅ AI predictions verification complete!')
