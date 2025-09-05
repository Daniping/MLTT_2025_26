# ===========================================
# MLTT_scraper.py - Version 2.1
# Objectif : Charger la page MLTT avec Playwright
# et mapper les logos aux noms d'équipes
# ===========================================

from playwright.sync_api import sync_playwright
from datetime import datetime
import json
import os

OUTPUT_JSON = "MLTT_matches.json"

# Mapping logo src → nom d'équipe
TEAM_MAPPING = {
    "687762138fa2e035f9b328c8_PRIMARY-BLACK-OUTLINE": "Princeton Revolution",
    "687762138fa2e035f9b328f1_PRIMARY-BLACK-OUTLINE": "New York Slice",
    "687762138fa2e035f9b32901_PRIMARY-WHITE-OUTLINE": "Carolina Gold Rush",
    "687762138fa2e035f9b32902_PRIMARY-BLACK-OUTLINE": "Florida Crocs",
    "687762138fa2e035f9b32905_PRIMARY-LOCKUP": "Atlanta Blazers",
    "687762138fa2e035f9b32a0f_AltLogo": "Portland Paddlers",
    "685e2c34b9486ae92f5afa74_PRIMARY-BLACK-OUTLINE": "Texas Smash",
    "687762138fa2e035f9b329c6_wind": "Chicago Wind",
    "687762138fa2e035f9b329c5_SPINNERS": "Los Angeles Spinners",
    "687762138fa2e035f9b328f2_PRIMARY-WHITE-OUTLINE": "Bay Area Blasters"
}

def fetch_matches():
    url = "https://mltt.com/league/schedule"
    matches = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)
        page.wait_for_timeout(5000)  # attendre que JS charge tout

        match_blocks = page.query_selector_all("div.future-match-single-top-wrap")

        for block in match_blocks:
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
                # Extraction de l'identifiant du logo
                base = os.path.basename(src).split(".")[0]
                name = TEAM_MAPPING.get(base, base)  # on prend le mapping sinon l'identifiant
                teams.append(name)

            team1 = teams[0] if len(teams) > 0 else "?"
            team2 = teams[1] if len(teams) > 1 else "?"

            # Ticket link
            ticket_el = block.query_selector("a.primary-btn-link-wrap")
            ticket = ticket_el.get_attribute("href") if ticket_el else None

            matches.append({
                "team1": team1,
                "team2": team2,
                "date": date_obj.isoformat() if date_obj else date_text,
                "venue": venue,
                "ticket": ticket
            })

        browser.close()

    return matches

if __name__ == "__main__":
    matches = fetch_matches()
    print(f"[OK] Nombre de matchs trouvés: {len(matches)}")
    for m in matches[:5]:  # aperçu 5 matchs
        print(m)

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(matches, f, ensure_ascii=False, indent=2)

    print(f"[OK] Données sauvegardées dans {OUTPUT_JSON}")