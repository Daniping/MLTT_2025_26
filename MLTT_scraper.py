# ===========================================
# MLTT_scraper.py - Scraper MLTT avec noms d'équipes
# Supprime doublons et écrit directement dans MLTT_2025_26_V5.ics
# ===========================================

from playwright.sync_api import sync_playwright

OUTPUT_FILE = "MLTT_2025_26_V5.ics"

# Dictionnaire complet des équipes MLTT
TEAM_MAPPING = {
    "687762138fa2e035f9b328c8": "Princeton Revolution",
    "687762138fa2e035f9b328f1": "New York Slice",
    "687762138fa2e035f9b32901": "Carolina Gold Rush",
    "687762138fa2e035f9b32902": "Florida Crocs",
    "687762138fa2e035f9b32905": "Houston Cosmos",
    "687762138fa2e035f9b32907": "Chicago Wind",
    "687762138fa2e035f9b32909": "Seattle Spinners",
    "687762138fa2e035f9b3290b": "Los Angeles Blaze",
    "687762138fa2e035f9b3290d": "Bay Area Breakers",
    "687762138fa2e035f9b3290f": "Boston Riptide",
    "687762138fa2e035f9b32911": "Philadelphia Power",
    "687762138fa2e035f9b32913": "Texas Cyclones",
    "687762138fa2e035f9b32915": "Denver Peaks",
    "687762138fa2e035f9b32917": "Las Vegas Lightning",
    "687762138fa2e035f9b32919": "San Diego Waves",
    "687762138fa2e035f9b3291b": "Orlando Orbit",
}

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
                ident = src.split("/")[-1].split("_")[0] if src else "?"
                # Conversion via dico
                name = TEAM_MAPPING.get(ident, alt if alt else ident)
                teams.append(name)

            team1 = teams[0] if len(teams) > 0 else "?"
            team2 = teams[1] if len(teams) > 1 else "?"
            matches.append({"team1": team1, "team2": team2})

        browser.close()

    return matches

if __name__ == "__main__":
    # On vide le fichier AVANT d’écrire
    open(OUTPUT_FILE, "w", encoding="utf-8").close()

    matches = fetch_matches()

    # Suppression des doublons
    unique_matches = []
    seen = set()
    for match in matches:
        key = (match["team1"], match["team2"])
        if key not in seen:
            seen.add(key)
            unique_matches.append(match)

    # Écriture dans le fichier du repo
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        for match in unique_matches:
            f.write(f"{match['team1']} vs {match['team2']}\n")

    print(f"[OK] {len(unique_matches)} matchs uniques ajoutés dans {OUTPUT_FILE}")