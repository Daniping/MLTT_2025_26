import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz

URL = "https://mltt.com/league/schedule"  # à adapter
OUT_ICS = "MLTT_2025_26_V5.ics"
TZ_PARIS = pytz.timezone("Europe/Paris")

resp = requests.get(URL)
resp.raise_for_status()
soup = BeautifulSoup(resp.text, "html.parser")

matches = []

for week_block in soup.select(".accordion-item"):
    # Date et lieu de la semaine
    week_info = week_block.select_one("h4.faq-head").text.strip()
    # Format exemple : "WEEK 3: Oct. 3-5, 2025 | Portland, OR | Oregon Convention Center"
    parts = week_info.split("|")
    if len(parts) >= 3:
        week_dates_str = parts[0].split(":")[1].strip()  # Oct. 3-5, 2025
        city = parts[1].strip()
        venue = parts[2].strip()
    else:
        continue

    for match_block in week_block.select(".future-match-single-wrap"):
        # Heure du match
        time_el = match_block.select_one(".future-match-game-title")
        if not time_el:
            continue
        time_str = time_el.text.strip()
        # Conversion en datetime Paris
        try:
            dt = datetime.strptime(time_str, "%b %d, %Y %I:%M %p")
            dt = pytz.utc.localize(dt).astimezone(TZ_PARIS)
        except:
            continue

        # Équipes
        teams = []
        for team_div in match_block.select(".future-match-single-clab-details"):
            name_div = team_div.select_one("div")
            if name_div and name_div.text.strip():
                teams.append(name_div.text.strip())

        if len(teams) != 2:
            continue

        matches.append({
            "team1": teams[0],
            "team2": teams[1],
            "datetime": dt,
            "city": city,
            "venue": venue
        })

# Écriture ICS
lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//MLTT//Schedule//FR"]

for m in matches:
    dt_str = m["datetime"].strftime("%Y%m%dT%H%M%S")
    lines.append("BEGIN:VEVENT")
    lines.append(f"SUMMARY:{m['team1']} vs {m['team2']}")
    lines.append(f"LOCATION:{m['venue']}, {m['city']}")
    lines.append(f"DTSTART;TZID=Europe/Paris:{dt_str}")
    lines.append(f"DTEND;TZID=Europe/Paris:{dt_str}")  # Durée à ajuster si tu veux
    lines.append("END:VEVENT")

lines.append("END:VCALENDAR")

with open(OUT_ICS, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"Wrote {OUT_ICS} with {len(matches)} events.")