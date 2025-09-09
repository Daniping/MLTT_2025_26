import os
from playwright.sync_api import sync_playwright

# Mapping hexadécimal → nom de l'équipe
TEAM_MAPPING = {
    "687762138fa2e035f9b328c8": "Princeton Revolution",
    "687762138fa2e035f9b328f1": "New York Slice",
    "687762138fa2e035f9b32901": "Carolina Gold Rush",
    "687762138fa2e035f9b32902": "Florida Crocs",
    # Ajouter toutes les équipes restantes ici
}

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto("https://mltt.com/league/schedule")

    # Récupération des blocs de matchs
    match_blocks = page.query_selector_all("div.schedule-game")

    print(f"[OK] Nombre de matchs trouvés: {len(match_blocks)}")

    for block in match_blocks:
        # Récupération des équipes
        team_imgs = block.query_selector_all("div.schedule-team-logo img")
        teams = []
        for img in team_imgs:
            src = img.get_attribute("src")
            base = os.path.basename(src).split(".")[0]
            base = base.replace("%20", "").split("(")[0].strip()
            name = TEAM_MAPPING.get(base, base)
            teams.append(name)
        
        # Affichage dans le run scraper
        print(f"{teams[0]} vs {teams[1]}")