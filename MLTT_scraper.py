from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from datetime import datetime
import pytz

URL = "https://mltt.com/league/schedule"
OUT_ICS = "MLTT_2025_26.ics"
TIMEZONE = "US/Pacific"

def fetch_page(url):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url)
        html = page.content()
        browser.close()
    return html

def parse_matches(html):
    soup = BeautifulSoup(html, "html.parser")
    matches = []

    match_blocks = soup.select("div.future-match-single-top-wrap")
    print(f"[DEBUG] Nombre de matchs trouvés: {len(match_blocks)}")

    for block in match_blocks:
        try:
            # Équipes via alt des logos
            logos = block.select("div.schedule-team-logo img")
            if len(logos) >= 2:
                team1 = logos[0].get("alt", "?").strip()
                team2 = logos[1].get("alt", "?").strip()
            else:
                team1 = team2 = "?"

            # Date et heure
            date_div = block.select_one("div.match-time-flex h3")
            date_str = date_div.get_text(strip=True) if date_div else "?"
            
            # Lieu
            venue_div = block.select_one("h3.future-match-game-title.mb-0")
            venue = venue_div.get_text(strip=True) if venue_div else "?"

            matches.append({
                "team1": team1,
                "team2": team2,
                "date": date_str,
                "venue": venue
            })
        except Exception as e:
            print(f"Erreur parsing match: {e}")
    return matches

def format_ics(matches):
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//MLTT//Schedule 2025-26//FR"
    ]
    tz = pytz.timezone(TIMEZONE)
    
    for m in matches:
        try:
            dt = datetime.strptime(m["date"], "%b %d, %Y %I:%M %p")
            dt = tz.localize(dt)
            dt_str = dt.strftime("%Y%m%dT%H%M%S")
            uid = f"{m['team1']}_vs_{m['team2']}_{dt_str}"
            lines.extend([
                "BEGIN:VEVENT",
                f"UID:{uid}",
                f"DTSTART;TZID={TIMEZONE}:{dt_str}",
                f"SUMMARY:{m['team1']} vs {m['team2']}",
                f"LOCATION:{m['venue']}",
                "END:VEVENT"
            ])
        except Exception as e:
            print(f"Erreur parsing date: {m['date']} ({e})")
    
    lines.append("END:VCALENDAR")
    return "\n".join(lines)

if __name__ == "__main__":
    html = fetch_page(URL)
    matches = parse_matches(html)
    print(f"[OK] Équipes récupérées ({len(matches)} matchs)")
    
    ics_content = format_ics(matches)
    with open(OUT_ICS, "w", encoding="utf-8") as f:
        f.write(ics_content)
    print(f"[OK] {OUT_ICS} écrit avec {len(matches)} événements.")