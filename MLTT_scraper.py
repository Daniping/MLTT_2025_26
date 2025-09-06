import json
import re
from playwright.sync_api import sync_playwright

# Fichier ICS où on enregistre les matchs
OUTPUT_FILE = "MLTT_2025_26_V5.ics"

# Mapping des équipes connues (identifiants -> noms)
TEAM_MAPPING = {
    "687762138fa2e035f9b328c8": "Princeton Revolution",
    "687762138fa2e035f9b328f1": "New York Slice",
    "687762138fa2e035f9b32901": "Carolina Gold Rush",
    "687762138fa2e035f9b32902": "Florida Crocs",
    "687762138fa2e035f9b32905": "Texas Smash",
    "687762138fa2e035f9b32a0f": "Seattle Spinners",
    "687762138fa2e035f9b329c6": "Bay Area Blasters",
    "687762138fa2e035f9b329c5": "Chicago Wind",
    "687762138fa2e035f9b328f2": "Los Angeles Stars",
}

def scrape_matches():
    url = "https://mltt.com/league/schedule"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)

        # On attend que les données soient présentes
        page.wait_for_selector("script#__NEXT_DATA__")

        # On récupère le JSON du site
        raw_json = page.query_selector("script#__NEXT_DATA__").inner_text()
        data = json.loads(raw_json)

        # Extraction des matchs
        matches = []
        try:
            events = data["props"]["pageProps"]["initialEvents"]
            for ev in events:
                t1 = ev.get("teamOne", {}).get("id")
                t2 = ev.get("teamTwo", {}).get("id")
                date = ev.get("startTime")
                venue = ev.get("venue", {}).get("name", "?")

                # Mapping des équipes (identifiants -> noms)
                def map_team(team_id):
                    if not team_id:
                        return "Unknown"
                    base = re.split(r"[_\-]", team_id)[0]
                    return TEAM_MAPPING.get(base, team_id)

                matches.append({
                    "team1": map_team(t1),
                    "team2": map_team(t2),
                    "date": date,
                    "venue": venue,
                })

        except Exception as e:
            print(f"[ERREUR] Impossible d’extraire les matchs : {e}")