# ===========================================
# MLTT_scraper.py - Version 2.0 (Playwright initial)
# Objectif : Charger la page MLTT avec Playwright
# pour exécuter le JavaScript et récupérer les matchs
# ===========================================

from playwright.sync_api import sync_playwright
from datetime import datetime
import json
import os

OUTPUT_JSON = "MLTT_matches.json"

def fetch_matches():
    url = "https://mltt.com/league/schedule"
    matches = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)
        page.wait_for_timeout(5000)  # attendre que JS charge tout

        # Récupération des blocs de matchs
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

            # Équipes (logo alt vide => faudra mapping ultérieur)
            team_imgs = block.query_selector_all("div.schedule-team-logo img")
            teams = []
            for img in team_imgs:
                alt = img.get_attribute("alt")
                src = img.get_attribute("src")
                teams.append(alt if alt else os.path.basename(src).split("_")[0])

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