# ===========================================
# MLTT_scraper.py - Extraction noms d'équipes
# - Vide le fichier au début
# - Récupère tous les noms des équipes depuis les logos
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
        page.wait_for_timeout(5000)  # attendre que JS charge tout

        match_blocks = page.query_selector_all("div.future-match-single-top-wrap")
        for block in match_blocks:
            team_imgs = block.query_selector_all("div.schedule-team-logo img")
            teams = []
            for img in team_imgs:
                name = img.get_attribute("alt") or "?"
                teams.append(name)

            if len(teams) >= 2:
                matches.append((teams[0], teams[1]))

        browser.close()
    return matches

if __name__ == "__main__":
    # Vider le fichier dès le début
    open(OUTPUT_FILE, "w", encoding="utf-8").close()

    # Récupérer tous les matchs
    matches = fetch_matches()

    # Supprimer les doublons tout en conservant l'ordre
    seen, unique_matches = set(), []
    for t1, t2 in matches:
        key = (t1, t2)
        if key not in seen:
            seen.add(key)
            unique_matches.append(key)

    # Écrire les matchs uniques dans le fichier
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        for t1, t2 in unique_matches:
            f.write(f"{t1} vs {t2}\n")

    print(f"[OK] {len(unique_matches)} matchs uniques écrits dans {OUTPUT_FILE}")