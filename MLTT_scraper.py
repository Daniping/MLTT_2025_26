# ===========================================
# MLTT_scraper.py - Scraper finalisé
# - Vide le fichier au tout début
# - Récupère tous les noms d'équipes directement
# - Récupère tous les matchs avec ces noms
# - Supprime les doublons
# - Écrit dans MLTT_2025_26_V5.ics
# ===========================================

from playwright.sync_api import sync_playwright

OUTPUT_FILE = "MLTT_2025_26_V5.ics"

TEAMS_URL = "https://mltt.com/teams"
SCHEDULE_URL = "https://mltt.com/league/schedule"

def fetch_team_names():
    """Récupère la liste des équipes depuis la page /teams"""
    teams = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(TEAMS_URL, timeout=60000)
        page.wait_for_timeout(5000)

        # Chaque équipe a un logo et un nom visible
        team_elements = page.query_selector_all("div.team-card h3.team-name")
        for el in team_elements:
            name = el.inner_text().strip()
            if name:
                teams.append(name)

        browser.close()
    return teams

def fetch_matches(team_names):
    """Récupère tous les matchs depuis /league/schedule en utilisant les noms connus"""
    matches = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(SCHEDULE_URL, timeout=60000)
        page.wait_for_timeout(5000)

        match_blocks = page.query_selector_all("div.future-match-single-top-wrap")
        for block in match_blocks:
            # Cherche tous les noms d'équipes dans le bloc
            teams_in_block = block.query_selector_all("h3.future-match-game-title")
            names = [t.inner_text().strip() for t in teams_in_block if t.inner_text().strip() in team_names]
            if len(names) >= 2:
                matches.append((names[0], names[1]))

        browser.close()
    return matches

if __name__ == "__main__":
    # 1. vider le fichier dès le début
    open(OUTPUT_FILE, "w", encoding="utf-8").close()

    # 2. récupérer les noms des équipes
    team_names = fetch_team_names()
    print(f"[OK] Équipes détectées : {team_names}")

    # 3. récupérer tous les matchs
    matches = fetch_matches(team_names)

    # 4. supprimer les doublons tout en conservant l'ordre
    seen, unique_matches = set(), []
    for t1, t2 in matches:
        key = (t1, t2)
        if key not in seen:
            seen.add(key)
            unique_matches.append(key)

    # 5. écrire les matchs uniques
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        for t1, t2 in unique_matches:
            f.write(f"{t1} vs {t2}\n")

    print(f"[OK] {len(unique_matches)} matchs uniques écrits dans {OUTPUT_FILE}") 