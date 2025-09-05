# ===========================================
# MLTT_scraper.py - Version 3.0 (ICS en clair)
# Objectif : Scraper les matchs MLTT et écrire
# directement dans MLTT_2025_26_V5.ICS
# ===========================================

from playwright.sync_api import sync_playwright
from datetime import datetime
import os

OUTPUT_FILE = "MLTT_2025_26_V5.ICS"  # Ton fichier existant

TEAM_MAPPING = {
    "687762138fa2e035f9b328c8": "Princeton Revolution",
    "687762138fa2e035f9b328f1": "New York Slice",
    "687762138fa2e035f9b32901": "Carolina Gold Rush",
    "687762138fa2e035f9b32902": "Florida Crocs",
    # ajouter d’autres mappings si besoin
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
            # Date
            date_el = block.query_selector("h3.future-match-game-title")
            date_text = date_el.inner_text().strip() if date_el else "?"

            try:
                date_obj = datetime.strptime(date_text, "%b %d, %Y %I:%M %p")
                date_str = date_obj.isoformat()
            except Exception:
                date_str = date_text

            # Lieu
            venue_el = block.query_selector("h3.city-state")
            venue = venue_el.inner_text().strip() if venue_el else "?"

            # Équipes
            team_imgs = block.query_selector_all("div.schedule-team-logo img")
            teams = []
            for img in team_imgs:
                alt = img.get_attribute("alt")
                src = img.get_attribute("src")
                base = os.path.basename(src).split("_")[0] if src else "?"
                team = TEAM_MAPPING.get(base, alt if alt else base)
                teams.append(team)

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

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for m in matches:
            f.write(f"{m['date']} - {m['team1']} vs {m['team2']} @ {m['venue']}\n")

    print(f"[OK] Données sauvegardées dans {OUTPUT_FILE}")