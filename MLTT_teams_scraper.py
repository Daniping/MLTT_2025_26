from playwright.sync_api import sync_playwright
import json
import os

OUTPUT_JSON = "MLTT_teams.json"

def fetch_teams():
    url = "https://mltt.com/league/schedule"
    teams_data = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)
        page.wait_for_timeout(5000)  # attendre que JS charge tout

        # Récupération des blocs de matchs
        match_blocks = page.query_selector_all("div.future-match-single-top-wrap")

        for block in match_blocks:
            team_imgs = block.query_selector_all("div.schedule-team-logo img")
            for img in team_imgs:
                alt = img.get_attribute("alt")
                src = img.get_attribute("src")
                teams_data.append({
                    "alt": alt if alt else "",
                    "src": src
                })

        browser.close()

    # Retirer les doublons
    unique_teams = {t["src"]: t for t in teams_data}.values()
    return list(unique_teams)

if __name__ == "__main__":
    teams = fetch_teams()
    print(f"[OK] Équipes récupérées ({len(teams)}):")
    for t in teams:
        print(t)

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(teams, f, ensure_ascii=False, indent=2)

    print(f"[OK] Données sauvegardées dans {OUTPUT_JSON}")