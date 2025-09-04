import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz

URL = "https://mltt.com/league/schedule"  # Remplace par la bonne URL si besoin
OUT_ICS = "MLTT_2025_26.ics"

def parse_match_date(date_str):
    """Parse une date au format 'Sep 5, 2025 4:00 PM PT' en datetime aware Paris"""
    try:
        date_clean = date_str.replace(" PT", "")
        dt_naive = datetime.strptime(date_clean, "%b %d, %Y %I:%M %p")
        pacific = pytz.timezone("US/Pacific")
        dt_aware = pacific.localize(dt_naive)
        return dt_aware
    except Exception as e:
        print(f"[WARN] Erreur parsing date: {date_str} -> {e}")
        return None

# Récupérer la page
resp = requests.get(URL)
resp.raise_for_status()
soup = BeautifulSoup(resp.text, "html.parser")
print(f"[INFO] Page récupérée, longueur HTML: {len(resp.text)}")

# Récupérer les blocs de matchs
match_blocks = soup.select(".future-match-single-top-wrap")
print(f"[DEBUG] Nombre de blocs match trouvés: {len(match_blocks)}")

matches = []

for block in match_blocks:
    try:
        # Équipes
        team_imgs = block.select(".schedule-team-logo img")
        team1 = team_imgs[0]["alt"] if len(team_imgs) > 0 else "?"
        team2 = team_imgs[1]["alt"] if len(team_imgs) > 1 else "?"

        # Date et heure
        date_elem = block.select_one(".future-match-game-title")
        date_str = date_elem.get_text(strip=True) if date_elem else ""
        dt = parse_match_date(date_str)
        if not dt:
            continue

        # Lieu
        venue_elem = block.select(".future-match-game-title")
        venue = venue_elem[1].get_text(strip=True) if len(venue_elem) > 1 else "?"

        matches.append({
            "team1": team1,
            "team2": team2,
            "dt": dt,
            "venue": venue,
            "city": "Paris"  # Ajuste si tu as la ville exacte
        })
    except Exception as e:
        print(f"[ERROR] Erreur match: {e}")

# Générer ICS
lines = [
    "BEGIN:VCALENDAR",
    "VERSION:2.0",
    "PRODID:-//MLTT 2025-26//EN"
]

paris = pytz.timezone("Europe/Paris")

for m in matches:
    dtstart = m["dt"].astimezone(paris).strftime("%Y%m%dT%H%M%S")
    lines.append("BEGIN:VEVENT")
    lines.append(f"SUMMARY:{m['team1']} vs {m['team2']}")
    lines.append(f"DTSTART;TZID=Europe/Paris:{dtstart}")
    lines.append(f"LOCATION:{m['venue']}, {m['city']}")
    lines.append("END:VEVENT")

lines.append("END:VCALENDAR")

with open(OUT_ICS, "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")

print(f"[OK] Fichier {OUT_ICS} écrit avec {len(matches)} événements.")