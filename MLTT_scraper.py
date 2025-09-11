# ===========================================
# MLTT_scraper.py - Extraction et composition des matchs
# - Vide le fichier au tout début
# - Récupère tous les noms des équipes depuis le site
# - Compose tous les matchs uniques possibles
# - Écrit dans MLTT_2025_26_V5.ics
# ===========================================

from playwright.sync_api import sync_playwright
from itertools import combinations

OUTPUT_FILE = "MLTT_2025_26_V5.ics"

def fetch_team_names():
    url = "https://mltt.com/league/schedule"
    teams = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)
        page.wait_for_timeout(5000)

        logo_imgs = page.query_selector_all("div.schedule-team-logo img")
        for img in logo_imgs:
            alt = img.get_attribute("alt")
            src = img.get_attribute("src") or ""
            ident = src.split("/")[-1].split("_")[0] if src else "?"
            name = alt if alt else ident
            teams.append(name)

        browser.close()

    return list(dict.fromkeys(teams))  # supprimer doublons

if __name__ == "__main__":
    # 1. vider le fichier dès le début
    open(OUTPUT_FILE, "w", encoding="utf-8").close()

    # 2. récupérer les noms uniques
    teams = fetch_team_names()

    # 3. composer tous les matchs possibles (chaque paire une seule fois)
    all_matches = list(combinations(teams, 2))

    # 4. écrire les matchs dans le fichier
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        for t1, t2 in all_matches:
            f.write(f"{t1} vs {t2}\n")

    print(f"[OK] {len(all_matches)} matchs composés et écrits dans {OUTPUT_FILE}")