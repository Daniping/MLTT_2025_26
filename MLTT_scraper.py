# ===========================================
# MLTT_scraper.py - Scraper MLTT minimal
# Écrit directement les matchs dans MLTT_2025_26_V5.ics
# Convertit les Hexas de 3 équipes en noms
# ===========================================

from playwright.sync_api import sync_playwright

OUTPUT_FILE = "MLTT_2025_26_V5.ics"

# Dictionnaire pour convertir les Hexas ciblés
TEAM_MAPPING = {
    "687762138fa2e035f9b328c8": "Princeton Revolution",
    "687762138fa2e035f9b328f1": "New York Slice",
    "687762138fa2e035f9b32901": "Carolina Gold Rush"
}

# -------------------------------
# Étape 0 : vider le fichier dès le départ
# -------------------------------
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    pass  # fichier vidé

# -------------------------------
# Étape 1 : récupération des matchs
# -------------------------------
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
                alt = img.get_attribute("alt")
                src = img.get_attribute("src")
                base = src.split("/")[-1].split("_")[0]  # identifiant du logo
                # conversion Hexa -> nom si présent dans le mapping
                name = TEAM_MAPPING.get(base, alt if alt else base)
                teams.append(name)

            team1 = teams[0] if len(teams) > 0 else "?"
            team2 = teams[1] if len(teams) > 1 else "?"
            matches.append({"team1": team1, "team2": team2})

        browser.close()

    return matches

# -------------------------------
# Étape 2 : écriture dans le fichier
# -------------------------------
if __name__ == "__main__":
    matches = fetch_matches()

    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        for match in matches:
            f.write(f"{match['team1']} vs {match['team2']}\n")

    print(f"[OK] {len(matches)} matchs ajoutés dans {OUTPUT_FILE}")