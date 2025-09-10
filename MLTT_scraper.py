# ===========================================
# MLTT_teams_scraper.py
# Récupère les noms des équipes MLTT depuis la page Teams
# ===========================================

from playwright.sync_api import sync_playwright

def fetch_team_names():
    url = "https://mltt.com/league/teams"
    team_names = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)
        page.wait_for_timeout(5000)  # attendre que JS charge

        # Chaque logo d’équipe est dans un <img alt="Nom équipe">
        logos = page.query_selector_all("div.team-logo img")
        for logo in logos:
            alt = logo.get_attribute("alt")
            if alt and alt not in team_names:
                team_names.append(alt.strip())

        browser.close()

    return team_names

if __name__ == "__main__":
    teams = fetch_team_names()
    print("[OK] Équipes détectées :")
    for t in teams:
        print("-", t)