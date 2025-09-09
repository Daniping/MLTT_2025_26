# MLTT_teams_scraper.py (adapté pour affichage des Hexa)

from playwright.sync_api import sync_playwright
import os

# Mapping Hexa -> Nom si besoin (pour l'instant on affiche juste les Hexa)
TEAM_MAPPING = {
    '687762138fa2e035f9b328c8': 'Princeton Revolution',
    '687762138fa2e035f9b328f1': 'New York Slice',
    '687762138fa2e035f9b32901': 'Carolina Gold Rush',
    '687762138fa2e035f9b32902': 'Florida Crocs',
    # ... Ajouter les autres équipes si nécessaire
}

URL = "https://mltt.com/league/schedule"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(URL)
    
    # On récupère tous les blocs de matchs comme dans le script qui a fonctionné
    match_blocks = page.query_selector_all("div.schedule-block")
    print(f"[OK] Nombre de matchs trouvés: {len(match_blocks)}")
    
    for block in match_blocks:
        # Récupération des logos/Hexa
        team_imgs = block.query_selector_all("div.schedule-team-logo img")
        teams = []
        for img in team_imgs:
            src = img.get_attribute("src")
            base = os.path.basename(src).split(".")[0]
            base = base.replace("%20", "").split("(")[0].strip()  # nettoyage
            teams.append(base)  # on affiche les Hexa

        # Récupération date, heure, lieu
        date_elem = block.query_selector("div.schedule-date")
        venue_elem = block.query_selector("div.schedule-venue")
        date_text = date_elem.inner_text() if date_elem else "?"
        venue_text = venue_elem.inner_text() if venue_elem else "?"

        # Affichage dans le run scraper
        print(f"{teams[0]} vs {teams[1]} - Date: {date_text}, Lieu: {venue_text}")

    browser.close()