import requests
import pandas as pd
from datetime import datetime

# URL de l'API MLTT
API_URL = "https://web.mltt.com/api/schedule?seasonId=0e4e3575-5ac3-4afc-ba87-3930103569f0"

# Plage de dates à filtrer (ex. 1ère semaine de septembre 2025)
START_DATE = datetime(2025, 9, 1)
END_DATE = datetime(2025, 9, 7, 23, 59, 59)

def fetch_schedule():
    """Récupère le calendrier depuis l'API MLTT."""
    response = requests.get(API_URL)
    response.raise_for_status()
    return response.json().get("matches", [])

def filter_matches(matches):
    """Filtre les matches selon la plage de dates."""
    filtered = []
    for match in matches:
        match_dt = datetime.fromisoformat(match.get("startDate"))
        if START_DATE <= match_dt <= END_DATE:
            filtered.append({
                "DateHeure": match.get("startDate"),
                "Lieu": match.get("venue", {}).get("name"),
                "Equipe Domicile": match.get("homeTeam", {}).get("name"),
                "Equipe Extérieure": match.get("awayTeam", {}).get("name")
            })
    return filtered

def main():
    matches = fetch_schedule()
    filtered_matches = filter_matches(matches)
    df = pd.DataFrame(filtered_matches)
    print(df)
    # Export CSV optionnel
    df.to_csv("mltt_sept_first_week.csv", index=False)

if __name__ == "__main__":
    main()
