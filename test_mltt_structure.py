import requests
import pandas as pd
from datetime import datetime

# URL de l'API DHLE (à remplacer par la vraie URL)
API_URL = "https://web.mltt.com/api/schedule?seasonId=0e4e3575-5ac3-4afc-ba87-3930103569f0"

# Plage de dates : tout septembre 2025
START_DATE = datetime(2025, 9, 1)
END_DATE = datetime(2025, 9, 30, 23, 59, 59)


def fetch_dhle():
    """Récupère les données DHLE depuis l'API."""
    response = requests.get(API_URL)
    response.raise_for_status()
    return response.json()  


def process_dhle(matches):
    dhle_data = []
    for match in matches:
        date = match.get("date")
        time = match.get("time")
        if date is None or time is None:
            continue  # ignore les matches sans date ou heure

        # Conversion en datetime pour filtrage
        try:
            match_dt = datetime.fromisoformat(date + "T" + time)
        except ValueError:
            continue  # ignore si le format est incorrect

        # Filtrage pour la première semaine de septembre 2025
        if START_DATE <= match_dt <= END_DATE:
            dhle_data.append({
                "D": date,
                "H": time,
                "L": match.get("venue", {}).get("name"),
                "E": f"{match.get('homeTeam')} vs {match.get('awayTeam')}"
            })
    return dhle_data


def main():
    matches = fetch_dhle()

    # Diagnostic : affiche les 5 premiers éléments pour voir la structure
    print("Extrait des 5 premiers matches :", matches[:5])

    dhle_table = pd.DataFrame(process_dhle(matches))
    print(dhle_table)
    dhle_table.to_csv("dhle_schedule_first_week_sept.csv", index=False)


if __name__ == "__main__":
    main()
