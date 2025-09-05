# ===========================================
# MLTT_teams_scraper.py - Version 1.1
# Objectif : Scruter le site MLTT et récupérer
# les équipes/logos via toutes les balises <img>
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
        page.wait_for_timeout(5000)  # attendre que JS charge

        # Récupération de toutes les balises <img>
        imgs = page.query_selector_all("img")

        for img in imgs:
            src = img.get_attribute("src") or ""
            alt = img.get_attribute("alt") or ""
            # On garde seulement ce qui semble lié aux logos d’équipes
            if "mltt" in src.lower() and (
                "logo" in src.lower()
                or "team" in src.lower()
                or "primary" in src.lower()
                or "spinners" in src.lower()
                or "wind" in src.lower()
                or "pong" in src.lower()
            ):
                teams.append({
                    "alt": alt.strip(),
                    "src": src.strip()
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