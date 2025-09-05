# ===========================================
# MLTT_scraper.py - Version artifact clair
# ===========================================

from playwright.sync_api import sync_playwright
from datetime import datetime
import json
import os

# Fichiers
OUTPUT_JSON = "MLTT_matches.json"
TEAMS_JSON = "MLTT_teams.json"

# Mapping identifiant -> nom (si teams.json existe)
if os.path.exists(TEAMS_JSON):
    with open(TEAMS_JSON, "r", encoding="utf-8") as f:
        team_data = json.load(f)
    TEAM_MAPPING = {}
    for t in team_data:
        src = t.get("src", "")
        base = os.path.basename(src).split(".")[0]
        TEAM_MAPPING[base] = t.get("alt") or base
else:
    TEAM_MAPPING = {}

def fetch_matches():
    url = "https://mltt.com/league/schedule"
    matches = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)
        page.wait_for_timeout(5000)  # attendre que JS charge tout

        match_blocks = page.query_selector_all("div.future-match-single-top-wrap")

        for block in match_blocks:
            # Date
            date_el = block.query_selector("h3.future-match-game-title")
            date_text = date_el.inner_text().strip() if date_el else "?"
            try:
                date_obj = datetime.strptime(date_text, "%b %d, %Y %I:%M %p")
                date_iso = date_obj.isoformat()
            except Exception:
                date_iso = date_text

            # Lieu
            venue_el = block.query_selector("h3.city-state")
            venue = venue_el.inner_text().strip() if venue_el else "?"

            # Équipes
            team_imgs = block.query_selector_all("div.schedule-team-logo img")
            teams = []
            for img in team_imgs:
                src = img.get_attribute("src")
                base = os.path.basename(src).split(".")[0]
                name = TEAM_MAPPING.get(base, base)
                teams.append(name)

            team1 = teams[0] if len(teams) > 0 else "?"
            team2 = teams[1] if len(teams) > 1 else "?"

            # Ticket
            ticket_el = block.query_selector("a.primary-btn-link-wrap")
            ticket = ticket_el.get_attribute("href") if ticket_el else None

            matches.append({
                "team1": team1,
                "team2": team2,
                "date": date_iso,
                "venue": venue,
                "ticket": ticket
            })

        browser.close()

    return matches

if __name__ == "__main__":
    matches = fetch_matches()
    print(f"[OK] Nombre de matchs trouvés: {len(matches)}")
    for m in matches[:10]:  # aperçu 10 matchs
        print(m)

    # Écrire JSON lisible
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(matches, f, ensure_ascii=False, indent=2)

    print(f"[OK] Données sauvegardées dans {OUTPUT_JSON}")