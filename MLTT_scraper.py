# ===========================================
# MLTT_scraper_final.py - Scraper stable
# ===========================================

from playwright.sync_api import sync_playwright

OUTPUT_FILE = "MLTT_2025_26_V5.ics"

# Liste officielle des 10 équipes (dans l'ordre des Hexas connus)
TEAM_NAMES = [
    "Princeton Revolution",
    "New York Slice",
    "Carolina Gold Rush",
    "Texas Smash",
    "Florida Crocs",
    "Los Angeles Beat",
    "Chicago Wind",
    "Bay Area Blasters",
    "Boston Spin",
    "Philadelphia Rollers"
]

# Hexas correspondant à l'ordre officiel
TEAM_HEXAS = [
    "687762138fa2e035f9b328c8",
    "687762138fa2e035f9b328f1",
    "687762138fa2e035f9b32901",
    "687762138fa2e035f9b32902",
    "687762138fa2e035f9b32903",
    "687762138fa2e035f9b32904",
    "687762138fa2e035f9b32905",
    "687762138fa2e035f9b32906",
    "687762138fa2e035f9b32907",
    "687762138fa2e035f9b32908"
]

# Mapping Hexa -> Nom
TEAM_MAPPING = dict(zip(TEAM_HEXAS, TEAM_NAMES))

def fetch_matches():
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
                name = TEAM_MAPPING.get(ident, ident)
                teams.append(name)
            if len(teams) >= 2:
                matches.append((teams[0], teams[1]))

        browser.close()
    return matches

if __name__ == "__main__":
    # 1. Vider le fichier dès le début
    open(OUTPUT_FILE, "w", encoding="utf-8").close()

    # 2. Récupérer tous les matchs
    matches = fetch_matches()

    # 3. Supprimer les doublons tout en conservant l'ordre
    seen, unique_matches = set(), []
    for t1, t2 in matches:
        key = (t1, t2)
        if key not in seen:
            seen.add(key)
            unique_matches.append(key)

    # 4. Écrire les matchs uniques
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        for t1, t2 in unique_matches:
            f.write(f"{t1} vs {t2}\n")

    print(f"[OK] {len(unique_matches)} matchs uniques écrits dans {OUTPUT_FILE}")