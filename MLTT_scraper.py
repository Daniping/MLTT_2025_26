# ===========================================
# MLTT_teams_scraper.py - Extraction équipes
# - Vide le fichier au début
# - Récupère tous les couples (hexa, nom)
# - Écrit dans MLTT_2025_26_V5.ics
# ===========================================

from playwright.sync_api import sync_playwright

OUTPUT_FILE = "MLTT_2025_26_V5.ics"

def fetch_teams():
    url = "https://mltt.com/teams"
    teams = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)
        page.wait_for_timeout(5000)

        # Chaque bloc d'équipe contient un logo + un nom
        blocks = page.query_selector_all("div.single-team-wrap")
        for block in blocks:
            img = block.query_selector("img")
            name_el = block.query_selector("h2, h3, .team-title, .title")

            if not img or not name_el:
                continue

            src = img.get_attribute("src") or ""
            ident = src.split("/")[-1].split("_")[0] if src else "?"
            name = name_el.inner_text().strip()

            teams.append((ident, name))

        browser.close()
    return teams


if __name__ == "__main__":
    # 1. vider le fichier dès le début
    open(OUTPUT_FILE, "w", encoding="utf-8").close()

    # 2. récupérer toutes les équipes
    teams = fetch_teams()

    # 3. écrire les couples hexa/nom
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        for ident, name in teams:
            f.write(f"{ident} = {name}\n")

    print(f"[OK] {len(teams)} équipes écrites dans {OUTPUT_FILE}")