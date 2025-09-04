from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from datetime import datetime
import pytz

URL = "https://mltt.com/league/schedule"
OUT_ICS = "MLTT_2025_26.ics"

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL)
        page.wait_for_timeout(5000)  # attendre 5 sec pour que le JS charge

        html = page.content()
        browser.close()

    soup = BeautifulSoup(html, "html.parser")
    matches = soup.select("div.future-match-single-top-wrap")

    print(f"[DEBUG] Nombre de matchs trouvés: {len(matches)}")

    events = []
    for match in matches:
        try:
            teams = match.select("div.schedule-team-logo img")
            if len(teams) >= 2:
                team1 = teams[0]["alt"] or "?"
                team2 = teams[1]["alt"] or "?"
            else:
                team1, team2 = "?", "?"

            date_block = match.select("h3.future-match-game-title")
            date_str = date_block[0].get_text(strip=True) + " " + date_block[1].get_text(strip=True)
            venue = date_block[2].get_text(strip=True)

            try:
                dt = datetime.strptime(date_str, "%b %d, %Y %I:%M %p %Z")
            except Exception:
                print(f"[WARN] Erreur parsing date: {date_str}")
                continue

            tz = pytz.timezone("US/Pacific")
            dt = tz.localize(dt)
            dt_utc = dt.astimezone(pytz.utc)

            event = {
                "summary": f"{team1} vs {team2}",
                "dtstart": dt_utc.strftime("%Y%m%dT%H%M%SZ"),
                "dtend": (dt_utc).strftime("%Y%m%dT%H%M%SZ"),
                "location": venue,
            }
            events.append(event)
        except Exception as e:
            print(f"[ERROR] {e}")

    # --- écrire ICS ---
    with open(OUT_ICS, "w") as f:
        f.write("BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//MLTT//EN\n")
        for ev in events:
            f.write("BEGIN:VEVENT\n")
            f.write(f"SUMMARY:{ev['summary']}\n")
            f.write(f"DTSTART:{ev['dtstart']}\n")
            f.write(f"DTEND:{ev['dtend']}\n")
            f.write(f"LOCATION:{ev['location']}\n")
            f.write("END:VEVENT\n")
        f.write("END:VCALENDAR\n")

    print(f"[OK] {OUT_ICS} écrit avec {len(events)} événements.")

if __name__ == "__main__":
    main()