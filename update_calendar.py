import requests
from bs4 import BeautifulSoup

MLTT_URL = "https://www.mltt.com/schedule"

def fetch_matches():
    response = requests.get(MLTT_URL)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    matches = []
    # Exemple à adapter selon la structure réelle de la page
    for match in soup.select(".match-card"):  # à vérifier/adapter
        date_el = match.select_one(".match-date")  # à vérifier
        time_el = match.select_one(".match-time")  # à vérifier
        teams_el = match.select_one(".match-teams")  # à vérifier
        location_el = match.select_one(".match-location")  # à vérifier

        if not all([date_el, time_el, teams_el, location_el]):
            continue  # Skip si une info manque

        date_str = date_el.text.strip()
        time_str = time_el.text.strip()
        teams = teams_el.text.strip()
        location = location_el.text.strip()

        print(f"Date : {date_str}, Heure : {time_str}, Équipes : {teams}, Lieu : {location}")

        matches.append({
            "date": date_str,
            "time": time_str,
            "teams": teams,
            "location": location
        })

    return matches

if __name__ == "__main__":
    fetch_matches()

