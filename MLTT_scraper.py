import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz

URL = "https://mltt.com/league/schedule"
OUT_ICS = "MLTT_2025_26_V5.ics"

# Récupérer la page
resp = requests.get(URL)
resp.raise_for_status()
soup = BeautifulSoup(resp.text, "html.parser")

matches = []

# Boucle sur chaque match
for match_block in soup.select(".future-match-single-wrap"):
    # Date et heure
    date_elem = match_block.select_one(".future-match-game-title")
    date_str = date_elem.text.strip() if date_elem else ""
    try:
        dt = datetime.strptime(date_str, "%b %d, %Y %I:%M %p")
        dt = pytz.timezone("America/Los_Angeles").localize(dt)  # Ajuster selon fuseau MLTT
        dt = dt.astimezone(pytz.timezone("Europe/Paris"))
    except:
        dt = None

    # Lieu
    city_elem = match_block.select_one(".city-state")
    venue_elem = match_block.select_one(".future-match-game-title + .city-state")
    city = city_elem.text.strip() if city_elem else "?"
    venue = venue_elem.text.strip() if venue_elem else "?"

    # Equipes
    team_divs = match_block.select(".future-match-single-clab-details div.schedule-team-logo + div")
    team1 = team_divs[0].text.strip() if len(team_divs) > 0 else "?"
    team2 = team_divs[1].text.strip() if len(team_divs) > 1 else "?"

    matches.append({
        "team1": team1,
        "team2": team2,
        "dt": dt,
        "venue": venue,
        "city": city
    })

# Génération ICS
lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//MLTT//Schedule//FR"]
for m in matches:
    if m["dt"]:
        dtstart = m["dt"].strftime("%Y%m%dT%H%M%S")
        lines.append("BEGIN:VEVENT")
        lines.append(f"SUMMARY:{m['team1']} vs {m['team2']}")
        lines.append(f"DTSTART;TZID=Europe/Paris:{dtstart}")
        lines.append(f"LOCATION:{m['venue']}, {m['city']}")
        lines.append("END:VEVENT")
lines.append("END:VCALENDAR")

with open(OUT_ICS, "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")

print(f"[OK] Fichier {OUT_ICS} écrit avec {len(matches)} événements.")