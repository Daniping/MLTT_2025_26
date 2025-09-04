import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz

URL = "https://mltt.com/league/schedule"
OUT_ICS = "MLTT_2025_26_V5.ics"
FR_TZ = pytz.timezone("Europe/Paris")

def fetch_html():
    r = requests.get(URL)
    r.raise_for_status()
    return r.text

def parse_matches(html):
    soup = BeautifulSoup(html, "html.parser")
    matches = []

    # Chaque semaine
    for week_div in soup.select("div.accordion-item"):
        header = week_div.select_one("h4.faq-head")
        if not header:
            continue
        week_info = header.get_text(strip=True)  # ex: "WEEK 3: Oct. 3-5, 2025 | Portland, OR | Oregon Convention Center"
        location = week_info.split("|")[-2].strip()
        venue = week_info.split("|")[-1].strip()

        # Chaque match
        for match_div in week_div.select("div.future-match-single-wrap"):
            date_h = match_div.select_one("h3.future-match-game-title")
            city_state = match_div.select_one("h3.city-state")
            teams = match_div.select("div.schedule-team-logo img")
            if len(teams) < 2 or not date_h:
                continue

            # Parse date
            try:
                dt = datetime.strptime(date_h.text.strip(), "%b %d, %Y %I:%M %p")
                dt = pytz.UTC.localize(dt).astimezone(FR_TZ)
            except Exception:
                continue

            team1 = teams[0]["alt"] if "alt" in teams[0].attrs else f"Team1"
            team2 = teams[1]["alt"] if "alt" in teams[1].attrs else f"Team2"

            matches.append({
                "dt": dt,
                "team1": team1,
                "team2": team2,
                "venue": venue,
                "city": location
            })
    return matches

def generate_ics(matches):
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//MLTT 2025-26//EN"
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
    lines.append("END:VCALENDAR")


def main():
    html = fetch_html()
    matches = parse_matches(html)
    generate_ics(matches)

if __name__ == "__main__":
    main()