# ===========================================
# MLTT_scraper.py - Version fonctionnelle
# Objectif : récupérer les matchs et les écrire
# dans MLTT_2025_26_V5.ics en clair
# ===========================================

from playwright.sync_api import sync_playwright
from datetime import datetime
import os

ICS_FILE = "MLTT_2025_26_V5.ics"

# Mapping des identifiants vers noms d'équipe
TEAM_MAPPING = {
    "687762138fa2e035f9b328c8": "Princeton Revolution",
    "687762138fa2e035f9b328f1": "New York Slice",
    "687762138fa2e035f9b32901": "Carolina Gold Rush",
    "687762138fa2e035f9b32902": "Florida Crocs",
    "687762138fa2e035f9b32905": "Team Alpha",
    "687762138fa2e035f9b32a0f": "Team Beta",
    "685e2c34b9486ae92f5afa74": "Team Gamma",
    "687762138fa2e035f9b329c6": "Wind",
    "687762138fa2e035f9b329c5": "Spinners",
    "687762138fa2e035f9b328f2": "Team Omega"
}

def fetch_matches():
    url = "https://mltt.com/league/schedule"
    matches = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)
        page.wait_for_timeout(5000)

        match_blocks = page.query_selector_all("div.future-match-single-top-wrap")
        for block in match_blocks:
            date_el = block.query_selector("h3.future-match-game-title")
            date_text = date_el.inner_text().strip() if date_el else "?"
            try:
                date_obj = datetime.strptime(date_text, "%b %d, %Y %I:%M %p")
                date_iso = date_obj.isoformat()
            except Exception:
                date_iso = date_text

            venue_el = block.query_selector("h3.city-state")
            venue = venue_el.inner_text().strip() if venue_el else "?"

            team_imgs = block.query_selector_all("div.schedule-team-logo img")
            teams = []
            for img in team_imgs:
                src = img.get_attribute("src")
                base_id = os.path.basename(src).split("_")[0]
                name = TEAM_MAPPING.get(base_id, base_id)
                teams.append(name)

            team1 = teams[0] if len(teams) > 0 else "?"
            team2 = teams[1] if len(teams) > 1 else "?"

            matches.append({
                "team1": team1,
                "team2": team2,
                "date": date_iso,
                "venue": venue
            })

        browser.close()
    return matches

def save_matches_to_ics(matches):
    with open(ICS_FILE, "a", encoding="utf-8") as f:  # 'a' pour append
        for m in matches:
            f.write(f"{m['date']} - {m['team1']} vs {m['team2']} @ {m['venue']}\n")

if __name__ == "__main__":
    matches = fetch_matches()
    print(f"[OK] Nombre de matchs trouvés: {len(matches)}")
    for m in matches[:5]:
        print(m)
    save_matches_to_ics(matches)
    print(f"[OK] Données sauvegardées dans {ICS_FILE}")