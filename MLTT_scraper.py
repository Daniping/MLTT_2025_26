import os
from playwright.sync_api import sync_playwright

TEAM_MAPPING = {
    "687762138fa2e035f9b328c8": "Princeton Revolution",
    "687762138fa2e035f9b328f1": "New York Slice",
    "687762138fa2e035f9b32901": "Carolina Gold Rush",
    "687762138fa2e035f9b32902": "Florida Crocs",
    # ... ajouter toutes les autres équipes ici
}

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto("https://mltt.com/league/schedule")

    # On récupère tous les blocs de matchs
    match_blocks = page.query_selector_all("div.schedule-game")

    matches = []

    for block in match_blocks:
        team_imgs = block.query_selector_all("div.schedule-team-logo img")
        teams = []
        for img in team_imgs:
            src = img.get_attribute("src")
            base = os.path.basename(src).split(".")[0]
            base = base.replace("%20", "").split("(")[0].strip()  # nettoyage
            name = TEAM_MAPPING.get(base, base)
            teams.append(name)
        
        date = block.query_selector("div.schedule-date").inner_text()
        time = block.query_selector("div.schedule-time").inner_text()
        venue = block.query_selector("div.schedule-venue").inner_text()

        match_info = f"{teams[0]} vs {teams[1]} - Date: {date}, Heure: {time}, Lieu: {venue}"
        matches.append(match_info)
        print(match_info)

    browser.close()