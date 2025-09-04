from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from datetime import datetime
import pytz

OUT_ICS = "MLTT_2025_26.ics"
URL = "https://mltt.com/league/schedule"

lines = [
    "BEGIN:VCALENDAR",
    "VERSION:2.0",
    "PRODID:-//MLTT 2025-26//EN"
]

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(URL)
    html = page.content()
    browser.close()

soup = BeautifulSoup(html, "html.parser")

matches = soup.select("div.schedule-for-mobile")  # bloc de chaque match

for match_block in matches:
    try:
        team_imgs = match_block.select("div.schedule-team-logo img")
        team1 = team_imgs[0]["alt"] if len(team_imgs) > 0 else "?"
        team2 = team_imgs[1]["alt"] if len(team_imgs) > 1 else "?"
        date_str = match_block.select_one("h3.future-match-game-title").get_text(strip=True)
        venue = match_block.select_one("h3.future-match-game-title.mb-0").get_text(strip=True)
        
        # conversion date
        try:
            dt = datetime.strptime(date_str, "%b %d, %Y %I:%M %p")
            dt = pytz.timezone("US/Pacific").localize(dt)
            dt_utc = dt.astimezone(pytz.utc)
            dt_str = dt_utc.strftime("%Y%m%dT%H%M%SZ")
        except Exception:
            dt_str = ""
        
        lines.append("BEGIN:VEVENT")
        lines.append(f"SUMMARY:{team1} vs {team2}")
        if dt_str:
            lines.append(f"DTSTART:{dt_str}")
        lines.append(f"LOCATION:{venue}")
        lines.append("END:VEVENT")
    except Exception as e:
        print("Erreur parsing match:", e)

lines.append("END:VCALENDAR")

with open(OUT_ICS, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"[OK] {OUT_ICS} écrit avec {len(matches)} matchs.")