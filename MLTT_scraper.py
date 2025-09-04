import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz

URL = "https://mltt.com/league/schedule"
OUT_ICS = "MLTT_2025_26_V6.ics"
FR_TZ = pytz.timezone("Europe/Paris")

def fetch_schedule():
    r = requests.get(URL)
    r.raise_for_status()
    return BeautifulSoup(r.text, "html.parser")

def parse_matches(soup):
    matches = []
    for week_div in soup.select(".accordion-item"):
        week_header = week_div.select_one("h4.faq-head").text.strip()
        week_name, location = week_header.split("|")[0:2]
        for match_div in week_div.select(".schedule-collection-item"):
            date_str = match_div.select_one(".future-match-game-title").text.strip()
            date_utc = datetime.strptime(date_str, "%b %d, %Y %I:%M %p")
            date_fr = pytz.utc.localize(date_utc).astimezone(FR_TZ)
            teams = [t.text.strip() for t in match_div.select(".schedule-team-logo + div")]
            venue = " | ".join([el.text.strip() for el in match_div.select(".city-state")])
            matches.append({
                "date": date_fr,
                "teams": teams,
                "venue": venue
            })
    return matches

def generate_ics(matches):
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//MLTT//2025-26 Schedule//FR"
    ]
    for m in matches:
        start = m["date"].strftime("%Y%m%dT%H%M%S")
        summary = " vs ".join(m["teams"])
        description = m["venue"]
        lines.extend([
            "BEGIN:VEVENT",
            f"DTSTART;TZID=Europe/Paris:{start}",
            f"SUMMARY:{summary}",
            f"DESCRIPTION:{description}",
            "END:VEVENT"
        ])
    lines.append("END:VCALENDAR")

    with open(OUT_ICS, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Wrote {OUT_ICS} with {len(matches)} events.")

def main():
    soup = fetch_schedule()
    matches = parse_matches(soup)
    generate_ics(matches)

if __name__ == "__main__":
    main()