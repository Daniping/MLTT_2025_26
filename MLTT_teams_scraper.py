from playwright.sync_api import sync_playwright
import json
import os

OUTPUT_JSON = "MLTT_teams.json"

def fetch_teams():
    url = "https://mltt.com/league/teams"  # ou la page qui liste toutes les équipes
    teams = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)
        page.wait_for_timeout(5000)  # attendre que JS charge tout

        team_blocks = page.query_selector_all("div.w-dyn-item")

        for block in team_blocks:
            link_el = block.query_selector("a.pages-link")
            href = link_el.get_attribute("href") if link_el else None

            img_el = block.query_selector("img")
            img_src = img_el.get_attribute("src") if img_el else None
            img_alt = img_el.get_attribute("alt") if img_el else None

            text_el = block.query_selector("div")
            name_text = text_el.inner_text().strip() if text_el else None

            teams.append({
                "id": href,
                "logo_src": img_src,
                "logo_alt": img_alt,
                "name": name_text
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