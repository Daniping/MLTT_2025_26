import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz

URL = "https://mltt.com/league/schedule"
OUT_ICS = "MLTT_2025_26.ics"

# Récupération de la page
resp = requests.get(URL)
resp.raise_for_status()
soup = BeautifulSoup(resp.text, "html.parser")

matches = soup.select(".future-match-single-top-wrap")

ics_events = []

for match in matches:
    # Récupérer les équipes
    teams = match.select(".future-match-single-details-wrap .schedule-team-logo img")
    team1 = teams[0].get("alt", "?") if len(teams) > 0 else "?"
    team2 = teams[1].get("alt", "?") if len(teams) > 1 else "?"

    # Infos du match
    details = match.select(".future-match-vs-wrap h3.future-match-game-title")
    date_time = details[0].get_text(strip=True) if len(details) > 0 else "?"
    timezone = details[1].get_text(strip=True) if len(details) > 1 else "?"
    location = details[2].get_text(strip=True) if len(details) > 2 else "?"

    # Conversion de la date
    try:
        dt_naive = datetime.strptime(date_time, "%b %d, %Y %I:%M %p")
        tz_map = {
            "PT": "US/Pacific",
            "ET": "US/Eastern",
            "CT": "US/Central",
            "MT": "US/Mountain"
        }
        tz = pytz.timezone(tz_map.get(timezone, "UTC"))
        dt = tz.localize(dt_naive)
        dt_end = dt + timedelta(hours=2)  # Match ≈ 2h
    except Exception as e:
        print(f"Erreur parsing date: {date_time} {timezone}")
        continue

    # Format ICS
    ics_event = f"""BEGIN:VEVENT
SUMMARY:{team1} vs {team2}
DTSTART:{dt.strftime("%Y%m%dT%H%M%S")}
DTEND:{dt_end.strftime("%Y%m%dT%H%M%S")}
LOCATION:{location}
END:VEVENT
"""
    ics_events.append(ics_event)

# Génération du fichier ICS
ics_content = "BEGIN:VCALENDAR\nVERSION:2.0\nCALSCALE:GREGORIAN\n"
ics_content += "".join(ics_events)
ics_content += "END:VCALENDAR\n"

with open(OUT_ICS, "w", encoding="utf-8") as f:
    f.write(ics_content)

print(f"[OK] Fichier {OUT_ICS} écrit avec {len(ics_events)} événements")