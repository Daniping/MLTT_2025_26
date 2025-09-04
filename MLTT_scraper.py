import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz

# --- Variables ---
OUT_ICS = "MLTT_2025_26_V5.ics"
with open("mltt_page.html", encoding="utf-8") as f:  # Page HTML récupérée
    soup = BeautifulSoup(f, "html.parser")

matches = []

# --- Extraction des matchs ---
for match_block in soup.select(".future-match-single-wrap"):
    try:
        dt_str = match_block.select_one(".future-match-game-title").text.strip()
        dt = datetime.strptime(dt_str, "%b %d, %Y %I:%M %p")
        dt = pytz.timezone("America/Los_Angeles").localize(dt).astimezone(pytz.timezone("Europe/Paris"))

        venue = match_block.select_one(".city-state:nth-of-type(1)").text.strip()
        city = match_block.select_one(".city-state:nth-of-type(2)").text.strip()

        team1 = match_block.select_one("div.w-dyn-list > div > div:nth-child(1) > a > div").text.strip()
        team2 = match_block.select_one("div.w-dyn-list > div > div:nth-child(2) > a > div").text.strip()

        matches.append({
            "dt": dt,
            "venue": venue,
            "city": city,
            "team1": team1,
            "team2": team2
        })
    except Exception as e:
        print(f"[WARN] Ignored a match due to error: {e}")

# --- Génération ICS ---
lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//MLTT//MLTT Calendar 2025-26//FR"]

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