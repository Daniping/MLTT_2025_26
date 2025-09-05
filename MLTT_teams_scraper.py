# ===========================================
# MLTT_teams_scraper.py
# Objectif : Récupérer les identifiants/logos des équipes MLTT
# ===========================================

from playwright.sync_api import sync_playwright
import json

OUTPUT_JSON = "MLTT_teams.json"

def fetch_teams():
    url = "https://mltt.com/league/schedule"
    teams = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)
        page.wait_for_timeout(5000)  # attendre que JS charge tout

        # Sélection de tous les logos d'équipes
        logo_elements = page.query_selector_all("div.schedule-team-logo img")

        for img in logo_elements:
            alt = img.get_attribute("alt")
            src = img.get_attribute("src")
            teams.append({
                "alt": alt if alt else "",
                "src": src
            })

        browser.close()

    return teams

if __name__ == "__main__":
    teams = fetch_teams()
    print(f"[OK] Équipes récupérées ({len(teams)}):")
    for t in teams:
        print(t)

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(teams, f, ensure_ascii=False, indent=2)

    print(f"[OK] Données sauvegardées dans {OUTPUT_JSON}")