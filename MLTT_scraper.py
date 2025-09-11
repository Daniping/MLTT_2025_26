# ===========================================
# MLTT_scraper.py - Extraction des équipes
# - Vide le fichier au tout début
# - Récupère tous les noms des équipes directement depuis le site
# - Supprime les doublons
# - Écrit les matchs dans MLTT_2025_26_V5.ics
# ===========================================

from playwright.sync_api import sync_playwright

OUTPUT_FILE = "MLTT_2025_26_V5.ics"

def fetch_team_names():
    url = "https://mltt.com/league/schedule"
    teams = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)
        page.wait_for_timeout(5000)  # attendre que JS charge tout

        # chercher toutes les images de logos
        logo_imgs = page.query_selector_all("div.schedule-team-logo img")
        for img in logo_imgs:
            alt = img.get_attribute("alt")
            src = img.get_attribute("src") or ""
            ident = src.split("/")[-1].split("_")[0] if src else "?"
            name = alt if alt else ident
            teams.append(name)

        browser.close()

    # supprimer doublons
    unique_teams = list(dict.fromkeys(teams))
    return unique_teams

if __name__ == "__main__":
    # 1. vider le fichier dès le début
    open(OUTPUT_FILE, "w", encoding="utf-8").close()

    # 2. récupérer les noms uniques
    teams = fetch_team_names()

    # 3. écrire les noms dans le fichier
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        for team in teams:
            f.write(f"{team}\n")

    print("[OK] Équipes détectées :")
    for team in teams:
        print(team)