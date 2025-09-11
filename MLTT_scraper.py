# ===========================================
# MLTT_scraper.py - Scraper équipes + matchs
# - Vide le fichier au début
# - Extrait les 10 équipes officielles
# - Extrait tous les matchs impliquant ces équipes
# - Supprime doublons
# - Écrit dans MLTT_2025_26_V5.ics
# ===========================================

from playwright.sync_api import sync_playwright

OUTPUT_FILE = "MLTT_2025_26_V5.ics"

def fetch_teams():
    url = "https://mltt.com/teams"
    teams = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)
        page.wait_for_timeout(5000)

        team_elements = page.query_selector_all("div.team-card-name")
        for el in team_elements:
            name = el.inner_text().strip()
            if name:
                teams.add(name)

        browser.close()
    return list(teams)

def fetch_matches(official_teams):
    url = "https://mltt.com/league/schedule"
    matches = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)
        page.wait_for_timeout(5000)

        match_blocks = page.query_selector_all("div.future-match-single-top-wrap")
        for block in match_blocks:
            team_imgs = block.query_selector_all("div.schedule-team-logo img")
            teams_in_match = []
            for img in team_imgs:
                alt = img.get_attribute("alt") or ""
                if alt in official_teams:
                    teams_in_match.append(alt)
            if len(teams_in_match) == 2:
                matches.append(tuple(teams_in_match))

        browser.close()
    return matches

if __name__ == "__main__":
    # 1. Vider le fichier dès le début
    open(OUTPUT_FILE, "w", encoding="utf-8").close()

    # 2. Récupérer les équipes officielles
    official_teams = fetch_teams()

    # 3. Récupérer les matchs
    matches = fetch_matches(official_teams)

    # 4. Supprimer doublons
    seen = set()
    unique_matches = []
    for t1, t2 in matches:
        key = (t1, t2)
        if key not in seen:
            seen.add(key)
            unique_matches.append(key)

    # 5. Écrire dans