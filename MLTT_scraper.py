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

# Parcourir chaque match block
for match_block in soup.select(".future-match-single-wrap"):
    children = match_block.find_all(recursive=False)  # enfants directs

    try:
        team1 = children[0].get_text(strip=True)
        team2 = children[1].get_text(strip=True)
        dt_text = children[2].get_text(strip=True)  # par ex. "Oct 3, 2025 4:00 PM"
        venue = children[3].get_text(strip=True)
        city = children[4].get_text(strip=True)

        dt = datetime.strptime(dt_text, "%b %d, %Y %I:%M %p")  # US format
        dt = pytz.timezone("America/Los_Angeles").localize(dt)  # changer si besoin
        dt = dt.astimezone(pytz.timezone("Europe/Paris"))

        matches.append({
            "team1": team1,
            "team2": team2,
            "dt": dt,
            "venue": venue,
            "city": city
        })
    except Exception as e:
        print("Erreur match:", e)

# Générer l'ICS
lines = [
    "BEGIN:VCALENDAR",
    "VERSION:2.0",
    "CALSCALE:GREGORIAN",
    "METHOD:PUBLISH"
]

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