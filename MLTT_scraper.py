# ===========================================
# MLTT_scraper.py - Version sans "ticket"
# ===========================================

from playwright.sync_api import sync_playwright
from datetime import datetime
import os

OUTPUT_FILE = "MLTT_2025_26_V5.ics"

TEAM_MAPPING = {
    "687762138fa2e035f9b328c8": "Princeton Revolution",
    "687762138fa2e035f9b328f1": "New York Slice",
    "687762138fa2e035f9b32901": "Carolina Gold Rush",
    "687762138fa2e035f9b32902": "Florida Crocs",
    "687762138fa2e035f9b32905": "Chicago Wind",
    "687762138fa2e035f9b32a0f": "Texas Smash",
    "685e2c34b9486ae92f5afa74": "Bay Area Spin",
    "687762138fa2e035f9b329c6": "Los Angeles Loop",
    "687762138fa2e035f9b329c5": "Boston Blades",
    "687762138fa2e035f9b328f2": "Seattle Spinners",
}

def fetch_matches():
    url = "https://mltt.com/league/schedule"
    matches = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)
        page.wait_for_timeout(5000)

        match_blocks = page.query_selector_all("div.future-match-single-top-wrap")

        for block in match_blocks:
            date_el = block.query_selector("h3.future-match-game-title")
            date_text = date_el.inner_text().strip() if date_el else "?"

            try:
                date_obj = datetime.strptime(date_text, "%b %d, %Y %I:%M %p")
                date_str = date_obj.isoformat()
            except Exception:
                date_str = date_text

            venue_el = block.query_selector("h3.city-state")
            venue = venue_el.inner_text().strip() if venue_el else "?"

            team_imgs = block.query_selector_all("div.schedule-team-logo img")
            teams = []
            for img in team_imgs:
                src = img.get_attribute("src") or ""
                base = os.path.basename(src).split("_")[0]
                teams.append(TEAM_MAPPING.get(base, base))

            team1 = teams[0] if len(teams) > 0 else "?"
            team2 = teams[1] if len(teams) > 1 else "?"

            matches.append({
                "team1": team1,
                "team2": team2,
                "date": date_str,
                "venue": venue
            })

        browser.close()
    return matches

if __name__ == "__main__":
    matches = fetch_matches()
    print(f"[OK] Nombre de matchs trouvés: {len(matches)}")

    # Écriture en clair dans le fichier (sans ticket)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for m in matches:
            line = f"{m['date']} | {m['team1']} vs {m['team2']} | {m['venue']}\n"
            f.write(line)

    print(f"[OK] Données sauvegardées en clair dans {OUTPUT_FILE}")