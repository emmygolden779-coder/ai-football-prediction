
import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('FOOTBALL_DATA_API_KEY')
BASE_URL = 'https://api.football-data.org/v4'

headers = {'X-Auth-Token': API_KEY}

print("Checking available competitions...\n")

try:
    # Get all available competitions
    comps_response = requests.get(f"{BASE_URL}/competitions", headers=headers)
    if comps_response.status_code == 200:
        comps_data = comps_response.json()
        print("=== AVAILABLE COMPETITIONS ===")
        for comp in comps_data['competitions']:
            print(f"- {comp['name']} ({comp['code']}) - ID: {comp['id']}")
        
        print("\n\n=== PREMIER LEAGUE STANDINGS ===")
        # Try to get PL standings (competition ID 2021)
        pl_response = requests.get(f"{BASE_URL}/competitions/2021/standings", headers=headers)
        if pl_response.status_code == 200:
            pl_standings = pl_response.json()
            for table in pl_standings['standings']:
                print(f"\n{table['type']} - {table['group'] if table['group'] else 'Overall'}:")
                for idx, team in enumerate(table['table'][:10], 1):
                    print(f"{idx}. {team['team']['name']} - {team['points']} points")

except Exception as e:
    print(f"Error: {e}")
