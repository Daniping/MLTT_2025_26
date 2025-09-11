# ===========================================
# MLTT_scraper.py - Extraction des matchs sans dictionnaire
# - Vide le fichier cible au début
# - Récupère tous les matchs via logos/alt
# - Supprime les doublons
# - Écrit dans MLTT_2025_26_V5.ics
# ===========================================

from playwright.sync_api import sync_playwright

OUTPUT_FILE = "MLTT_2025_26_V5.ics"

def fetch_matches():
    url = "https://mltt.com/league/schedule"
    matches = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)
        page.wait_for_timeout(5000)  # attendre le chargement JS

        match_blocks = page.query_selector_all("div.future-match-single-top-wrap")
        for block in match_blocks:
            team_imgs = block.query_selector_all("div.schedule-team-logo img")
            teams = []
            for img in team_imgs:
                alt = img.get_attribute("alt")
                src = img.get_attribute("src") or ""
                ident = src.split("/")[-1].split("_")[0] if src else "?"
                # utiliser alt si présent sinon ident issu du src
                name = alt if alt else ident
                teams.append(name)

            if len(teams) >= 2:
                matches.append((teams[0], teams[1]))

        browser.close()
    return matches

if __name__ == "__main__":
    # 1. Vider le fichier cible au début
    open(OUTPUT_FILE, "w", encoding="utf-8").close()

    # 2. Récupérer tous les matchs
    matches = fetch_matches()

    # 3. Supprimer doublons tout en conservant l'ordre
    seen, unique_matches = set(), []
    for t1, t2 in matches:
        key = (t1, t2)
        if