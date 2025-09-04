import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz

URL = "https://www.mltt.com/schedule"
response = requests.get(URL)
soup = BeautifulSoup(response.text, "html.parser")

matches = []

for block in soup.select(".future-match-single-top-wrap"):
    try:
        # Équipes (logo + alt vide → on prend le src du logo comme identifiant unique si besoin)
        team1 = block.select_one(".future-match-single-details-wrap:first-child img")
        team2 = block.select_one(".future-match-single-details-wrap:last-child img")
        team1_name = team1["alt"] if team1 and team1.get("alt") else "?"
        team2_name = team2["alt"] if team2 and team2.get("alt") else "?"

        # Date / lieu
        date_block = block.select_one(".match-time-flex h3")
        if date_block:
            date_time = date_block.get_text(strip=True)

            # Nettoyer fuseaux horaires possibles
            for tz in ["PT", "ET", "CT", "MT"]:
                date_time = date_time.replace(tz, "").strip()

            # Parser date naive
            dt_naive = datetime.strptime(date_time, "%b %d, %Y %I:%M %p")

            # Ajouter timezone US/Pacific (par défaut MLTT joue en Californie)
            pacific = pytz.timezone("US/Pacific")
            dt = pacific.localize(dt_naive)
        else:
            dt = None

        # Lieu
        venue_block = block.select_one(".future-match-game-title.mb-0")
        venue = venue_block.get_text(strip=True) if venue_block else "?"

        matches.append({
            "team1": team1_name,
            "team2": team2_name,
            "date": dt,
            "venue": venue
        })

    except Exception as e:
        print("Erreur parsing match:", e)

for m in matches:
    print(f"{m['team1']} vs {m['team2']} - {m['date']} @ {m['venue']}")