import requests
import pandas as pd
from datetime import datetime

# URL de l'API DHLE (à remplacer par la vraie URL)
API_URL = "https://web.mltt.com/api/schedule?seasonId=0e4e3575-5ac3-4afc-ba87-3930103569f0"


# Définir la plage de dates : 1ère semaine de septembre 2025
START_DATE = datetime(2025, 9, 1)
END_DATE = datetime(2025, 9, 7, 23, 59, 59)

def fetch_dhle():
    """Récupère les données DHLE depuis l'API."""
    response = requests.get(API_URL)
    response.raise_for_status()
    return response.json()  


def process_dhle(matches):
    """Filtre les matches et transforme les données en tableau avec D, H, L, E."""
    dhle_data = []
    for match in matches:
        match_dt = datetime.fromisoformat(match.get("date") + "T" + match.get("time"))
        if START_DATE <= match_dt <= END_DATE:
            dhle_data.append({
                "D": match.get("date"),
                "H": match.get("time"),
                "L": match.get("venue", {}).get("name"),
                "E": f"{match.get('homeTeam')} vs {match.get('awayTeam')}"
            })
    return dhle_data

def main():
    matches = fetch_dhle()
    dhle_table = pd.DataFrame(process_dhle(matches))
    print(dhle_table)
    dhle_table.to_csv("dhle_schedule_first_week_sept.csv", index=False)

if __name__ == "__main__":
    main()
