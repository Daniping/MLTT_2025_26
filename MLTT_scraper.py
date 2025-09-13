# ===========================================
# MLTT_scraper.py - Scraper finalisé
# - Vide le fichier au tout début
# - Récupère dynamiquement tous les noms d'équipes
# - Supprime les doublons
# - Écrit dans MLTT_2025_26_V5.ics
# ===========================================

from playwright.sync_api import sync_playwright

OUTPUT_FILE = "MLTT_2025_26_V5.ics"

def fetch_team_mapping():
    url = "https://mltt.com/teams"
    mapping = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)
        page.wait_for_timeout(5000)
        team_divs = page.query_selector_all("div.team-card")  # exemple de sélecteur
        for div in team_divs:
            img = div.query_selector("img")
            if img:
                src = img.get_attribute("src")
                ident = src.split("/")[-1].split("_")[0]
                name = div.inner_text().strip()  # récupère le nom visible de l'équipe
                mapping[ident] = name
        browser.close()
    return mapping

def fetch_matches(team_mapping):
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
            teams = []
            for img in team_imgs:
                src = img.get_attribute("src") or ""
                ident = src.split("/")[-1].split("_")[0] if src else "?"
                name = team_mapping.get(ident, ident)
                teams.append(name)
            if len(teams) >= 2:
                matches.append((teams[0], teams[1]))
        browser.close()
    return matches

if __name__ == "__main__":
    # 1. vider le fichier dès le début
    open(OUTPUT_FILE, "w", encoding="utf-8").close()

    # 2. récupérer le mapping Hexa → nom
    team_mapping = fetch_team_mapping()

    # 3. récupérer tous les matchs
    matches = fetch_matches(team_mapping)

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