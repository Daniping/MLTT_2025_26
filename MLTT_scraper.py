# ===========================================
# MLTT_scraper_teams.py
# - Récupère la liste (hexa, nom d'équipe)
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

        # Chaque bloc équipe
        team_blocks = page.query_selector_all("div.w-dyn-item")

        for block in team_blocks:
            img = block.query_selector("img")
            if not img:
                continue

            src = img.get_attribute("src") or ""
            ident = src.split("/")[-1].split("_")[0]

            # Le nom de l’équipe (souvent dans h2 ou h3)
            name_el = block.query_selector("h2, h3, .team-name, .title")
            team_name = name_el.inner_text().strip() if name_el else ""

            if ident and team_name:
                teams.append((ident, team_name))

        browser.close()

    return teams


if __name__ == "__main__":
    # Vider le fichier au début
    open(OUTPUT_FILE, "w", encoding="utf-8").close()

    teams = fetch_teams()

    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        for ident, name in teams:
            f.write(f"{ident} = {name}\n")

    print(f"[OK] {len(teams)} équipes écrites dans {OUTPUT_FILE}")