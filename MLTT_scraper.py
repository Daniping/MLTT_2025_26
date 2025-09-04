import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz

URL = "https://mltt.com/league/schedule"  # Remplace par la bonne URL si besoin
OUT_ICS = "MLTT_2025_26_V5.ics"

# Récupérer la page
resp = requests.get(URL)
resp.raise_for_status()
soup = BeautifulSoup(resp.text, "html.parser")

matches = []

# Exemple de sélecteurs pour récupérer dates, lieux et équipes
for match_block in soup.select(".future-match-single-wrap"):
    date_text = match_block.select_one(".future-match-game-title").text.strip()
    venue_text = match_block.select_one(".city-state").text.strip()
    teams = [t.text.strip() for t in match_block.select("div.schedule-team-logo + div")]

    dt = datetime.strptime(date_text, "%b %d, %Y %I:%M %p")  # ex: "Oct 3, 2025 4:00 PM"
    dt = pytz.timezone("America/Los_Angeles").localize(dt)   # à adapter si nécessaire
    dt_paris = dt.astimezone(pytz.timezone("Europe/Paris"))

    match = {
        "dt": dt_paris,
        "venue": venue_text,
        "city": "",  # ajouter si séparé
        "team1": teams[0] if len(teams) > 0 else "Unknown",
        "team2": teams[1] if len(teams) > 1 else "Unknown",
    }
    matches.append(match)

# Générer ICS
lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//MLTT//2025-26 Schedule//FR"]

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