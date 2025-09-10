# ===========================================
# MLTT_teams.py - Extraction des noms d'équipes en clair
# ===========================================

from playwright.sync_api import sync_playwright

def fetch_team_names():
    url = "https://mltt.com/league/schedule"
    team_names = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)
        page.wait_for_timeout(5000)

        # On récupère tous les logos
        team_imgs = page.query_selector_all("div.schedule-team-logo img")

        for img in team_imgs:
            alt = img.get_attribute("alt")
            if alt:
                team_names.add(alt.strip())

        browser.close()

    return sorted(team_names)

if __name__ == "__main__":
    teams = fetch_team_names()
    print("[OK] Équipes détectées :")
    for t in teams:
        print("-", t)