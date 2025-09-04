from playwright.sync_api import sync_playwright
from ics import Calendar, Event
from datetime import datetime
import pytz
import os

URL = "https://mltt.com/league/schedule"
OUT_ICS = "MLTT_2025_26.ics"
TIMEZONE = "US/Pacific"

def main():
    calendar = Calendar()
    matches = []

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(URL)
        page.wait_for_selector(".future-match-single-top-wrap", timeout=10000)  # Attendre que les matchs soient chargés

        match_blocks = page.query_selector_all(".schedule-for-mobile > .future-match-single-top-wrap")
        print(f"[DEBUG] Nombre de matchs trouvés: {len(match_blocks)}")

        for block in match_blocks:
            try:
                teams = block.query_selector_all(".schedule-team-logo + div")
                team1 = teams[0].inner_text().strip() if len(teams) > 0 else "?"
                team2 = teams[1].inner_text().strip() if len(teams) > 1 else "?"
                
                date_text = block.query_selector(".future-match-game-title").inner_text().strip()
                venue = block.query_selector("h3.mb-0").inner_text().strip()
                
                matches.append({
                    "team1": team1,
                    "team2": team2,
                    "date": date_text,
                    "venue": venue
                })
            except Exception as e:
                print(f"[WARN] Erreur parsing match: {e}")

        browser.close()

    # Convertir les dates et générer le .ics
    tz = pytz.timezone(TIMEZONE)
    for m in matches:
        try:
            dt = datetime.strptime(m["date"], "%b %d, %Y %I:%M %p")
            dt = tz.localize(dt)

            event = Event()
            event.name = f"{m['team1']} vs {m['team2']}"
            event.begin = dt
            event.location = m["venue"]
            calendar.events.add(event)
        except Exception as e:
            print(f"[WARN] Erreur parsing date: {m['date']} - {e}")

    with open(OUT_ICS, "w", encoding="utf-8") as f:
        f.writelines(calendar)
    print(f"[OK] {OUT_ICS} écrit avec {len(calendar.events)} événements.")

if __name__ == "__main__":
    main()