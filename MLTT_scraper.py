import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz

URL = "https://www.mltt.com/league/schedule"
OUT_ICS = "MLTT_2025_26_V5.ics"
PARIS_TZ = pytz.timezone("Europe/Paris")

# --- Récupération de la page ---
resp = requests.get(URL)
resp.raise_for_status()
soup = BeautifulSoup(resp.text, "html.parser")

matches = []

# --- Extraction des matchs ---
for match_block in soup.select(".future-match-single-wrap"):
    try:
        # Heure et lieu
        date_str = match_block.select_one(".future-match-game-title").get_text(strip=True)
        dt_utc = datetime.strptime(date_str, "%b %d, %Y %I:%M %p").replace(tzinfo=pytz.UTC)
        dt_paris = dt_utc.astimezone(PARIS_TZ)
        
        city = match_block.select_one(".future-match-game-title.city-state").get_text(strip=True)
        venue = match_block.select(".future-match-game-title.city-state")[1].get_text(strip=True)
        
        # Équipes
        logos = match_block.select(".future-match-single-clab-details .schedule-team-logo img")
        team1 = logos[0]["alt"]
        team2 = logos[1]["alt"]

        matches.append({
            "dt": dt_paris,
            "city": city,
            "venue": venue,
            "team1": team1,
            "team2": team2
        })
    except Exception as e:
        print(f"[WARN] Ignored a match block: {e}")

# --- Génération ICS ---
lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//MLTT//MLTT Calendar//FR"]

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