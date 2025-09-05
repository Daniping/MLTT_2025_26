# ===========================================
# MLTT_scraper.py - Version 5.0
# Objectif : Récupérer les matchs MLTT et
# les écrire dans MLTT_2025_26_V5.ICS
# ===========================================

from playwright.sync_api import sync_playwright
from datetime import datetime
import os

OUTPUT_ICS = "MLTT_2025_26_V5.ICS"

TEAM_MAPPING = {
    "687762138fa2e035f9b328c8": "Princeton Revolution",
    "687762138fa2e035f9b328f1": "New York Slice",
    "687762138fa2e035f9b32901": "Carolina Gold Rush",
    "687762138fa2e035f9b32902": "Florida Crocs",
    "687762138fa2e035f9b32905": "Atlanta Blazers",
    "687762138fa2e035f9b32a0f": "Portland Paddlers",
    "685e2c34b9486ae92f5afa74": "Texas Smash",
    "687762138fa2e035f9b329c6": "Los Angeles Spinners",
    "687762138fa2e035f9b329c5": "Bay Area Blasters",
    "687762138fa2e035f9b328f2": "Chicago Wind"
}

def fetch_matches():
    url = "https://mltt.com/league/schedule"
    matches = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)
        page.wait_for_timeout(5000)  # attendre JS

        blocks = page.query_selector_all("div.future-match-single-top-wrap")

        for block in blocks:
            # Date
            date_el = block.query_selector("h3.future-match-game-title")
            date_text = date_el.inner_text().strip() if date_el else "?"
            try:
                date_obj = datetime.strptime(date_text, "%b %d, %Y %I:%M %p")
            except Exception:
                date_obj = None

            # Lieu
            venue_el = block.query_selector("h3.city-state")
            venue = venue_el.inner_text().strip() if venue_el else "?"

            # Équipes
            team_imgs = block.query_selector_all("div.schedule-team-logo img")
            teams = []
            for img in team_imgs:
                src = img.get_attribute("src")
                base = os.path.basename(src).split("_")[0]
                name = TEAM_MAPPING.get(base, base)
                teams.append(name)

            team1 = teams[0] if len(teams) > 0 else "?"
            team2 = teams[1] if len(teams) > 1 else "?"

            # Ticket
            ticket_el = block.query_selector("a.primary-btn-link-wrap")
            ticket = ticket_el.get_attribute("href") if ticket_el else None

            matches.append({
                "team1": team1,
                "team2": team2,
                "date": date_obj,
                "venue": venue,
                "ticket": ticket
            })

        browser.close()
    return matches

def write_ics(matches):
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//MLTT Scraper//EN"
    ]
    for m in matches:
        if not m["date"]:
            continue
        lines += [
            "BEGIN:VEVENT",
            f"SUMMARY:{m['team1']} vs {m['team2']}",
            f"DTSTART:{m['date'].strftime('%Y%m%dT%H%M%S')}",
            f"LOCATION:{m['venue']}",
            f"DESCRIPTION:Tickets: {m['ticket']}" if m['ticket'] else "DESCRIPTION:",
            "END:VEVENT"
        ]
    lines.append("END:VCALENDAR")

    with open(OUTPUT_ICS, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"[OK] {len(matches)} matchs écrits dans {OUTPUT_ICS}")

if __name__ == "__main__":
    matches = fetch_matches()
    write_ics(matches)