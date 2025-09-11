# ===========================================
# MLTT_scraper.py - Extraction des matchs simplifiée
# - Vide le fichier cible au début
# - Récupère tous les matchs via logos
# - Convertit Hexas connus en noms
# - Supprime les doublons
# - Écrit dans MLTT_2025_26_V5.ics
# ===========================================

from playwright.sync_api import sync_playwright

OUTPUT_FILE = "MLTT_2025_26_V5.ics"

# Dictionnaire officiel des 10 équipes connues
TEAM_MAPPING = {
    "687762138fa2e035f9b328c8": "Princeton Revolution",
    "687762138fa2e035f9b328f1": "New York Slice",
    "687762138fa2e035f9b32901": "Carolina Gold Rush",
    "687762138fa2e035f9b32909": "Texas Smash",
    "687762138fa2e035f9b32902": "Florida Crocs",
    "687762138fa2e035f9b3290b": "Los Angeles Beat",
    "687762138fa2e035f9b3290f": "Chicago Wind",
    "687762138fa2e035f9b3290d": "Bay Area Blasters",
    "687762138fa2e035f9b32774": "Boston Spin",
    "687762138fa2e035f9b32787": "Philadelphia Rollers",
}

def fetch_matches():
    url = "https://mltt.com/league/schedule"
    matches = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)
        page.wait_for_timeout(5000)  # attendre le chargement JS

        # chaque bloc correspond à un match
        match_blocks = page.query_selector_all("div.future-match-single-top-wrap")
        for block in match_blocks:
            team_imgs = block.query_selector_all("div.schedule-team-logo img")
            teams = []
            for img in team_imgs:
                src = img.get_attribute("src") or ""
                ident = src.split("/")[-1].split("_")[0] if src else "?"
                name = TEAM_MAPPING.get(ident, ident)  # convertir si connu
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
        if key not in seen:
            seen.add(key)
            unique_matches.append(key)

    # 4. Écrire les matchs finaux dans le fichier
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        for t1, t2 in unique_matches:
            f.write(f"{t1} vs {t2}\n")

    print(f"[OK] {len(unique_matches)} matchs uniques écrits dans {OUTPUT_FILE}")