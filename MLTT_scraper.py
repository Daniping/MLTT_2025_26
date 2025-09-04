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

# Exemple : on récupère les blocs de match (à ajuster selon le HTML)
for match_block in soup.select(".future-match-single-wrap"):
    # Date et heure
    date_str = match_block.select_one(".match-date").get_text(strip=True)
    time_str = match_block.select_one(".match-time").get_text(strip=True)
    dt = datetime.strptime(f"{date_str} {time_str}", "%b %d, %Y %I:%M %p")
    
    # Lieu
    venue = match_block.select_one(".match-venue").get_text(strip=True)
    city = match_block.select_one(".match-city").get_text(strip=True)
    
    # Équipes
    team_divs = match_block.select("div.w-dyn-item > a.pages-link")
    if len(team_divs) >= 2:
        team1 = team_divs[0].select_one("div").get_text(strip=True)
        team2 = team_divs[1].select_one("div").get_text(strip=True)
    else:
        team1 = team2 = "?"
    
    matches.append({
        "dt": dt,
        "venue": venue,
        "city": city,
        "team1": team1,
        "team2": team2
    })

# Créer le fichier ICS
lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//MLTT//2025//FR"]

for m in matches:
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