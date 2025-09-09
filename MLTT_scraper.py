# MLTT_scraper.py
import os
from playwright.sync_api import sync_playwright

# Mapping des IDs des logos vers les noms d'équipes
TEAM_MAPPING = {
    "687762138fa2e035f9b328c8": "Princeton Revolution",
    "687762138fa2e035f9b328f1": "New York Slice",
    "687762138fa2e035f9b32901": "Carolina Gold Rush",
    "687762138fa2e035f9b32902": "Florida Crocs",
    # Ajouter les autres identifiants si nécessaire
}

URL_SCHEDULE = "https://mltt.com/league/schedule"

matches = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(URL_SCHEDULE)
    page.wait_for_selector("div.schedule-block")  # attends que le calendrier charge

    blocks = page.query_selector_all("div.schedule-block")
    for block in blocks:
        # Récupération des logos / noms des équipes
        team_imgs = block.query_selector_all("div.schedule-team-logo img")
        teams = []
        for img in team_imgs:
            src = img.get_attribute("src")
            base = os.path.basename(src).split(".")[0]
            base = base.replace("%20", "").split("(")[0].strip()
            name = TEAM_MAPPING.get(base, base)
            teams.append(name)

        if len(teams) == 2:
            # Récupération de la date / lieu
            date_elem = block.query_selector("div.schedule-date")
            venue_elem = block.query_selector("div.schedule-venue")
            date = date_elem.inner_text().strip() if date_elem else "?"
            venue = venue_elem.inner_text().strip() if venue_elem else "?"
            
            match = {
                "team1": teams[0],
                "team2": teams[1],
                "date": date,
                "venue": venue
            }
            matches.append(match)
            print(match)

    browser.close()

print(f"[OK] Nombre de matchs trouvés: {len(matches)}")