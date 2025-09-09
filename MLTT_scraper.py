# ===========================================
# MLTT_scraper.py - Scraper finalisé
# - Vide le fichier au tout début
# - Convertit tous les hexas en noms d'équipes
# - Supprime les doublons
# - Écrit dans MLTT_2025_26_V5.ics
# ===========================================

from playwright.sync_api import sync_playwright

OUTPUT_FILE = "MLTT_2025_26_V5.ics"

# Dictionnaire complet des 10 équipes MLTT
TEAM_MAP = {
    "687762138fa2e035f9b328c8": "Princeton Revolution",
    "687762138fa2e035f9b328f1": "New York Slice",
    "687762138fa2e035f9b32901": "Carolina Gold Rush",
    "687762138fa2e035f9b32902": "Texas Smash",
    "687762138fa2e035f9b32903": "Florida Crocs",
    "687762138fa2e035f9b32904": "Los Angeles Beat",
    "687762138fa2e035f9b32905": "Chicago Wind",
    "687762138fa2e035f9b32906": "Bay Area Blasters",
    "687762138fa2e035f9b32907": "Boston Spin",
    "687762138fa2e035f9b32908": "Philadelphia Rollers",
    "687762138fa2e035f9b32909": "Atlanta Loop",
    "687762138fa2e035f9b3290a": "Seattle Bounce",
    "687762138fa2e035f9b3290b": "Denver Smashers",
    "687762138fa2e035f9b3290c": "Las Vegas Flick",
    "687762138fa2e035f9b3290d": "San Diego Paddle",
    "687762138fa2e035f9b3290e": "Houston Spin Masters"
}

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
                alt = img.get_attribute("alt")
                src = img.get_attribute("src") or ""
                ident = src.split("/")[-1].split("_")[0] if src else "?"
                name = TEAM_MAPPING.get(ident, alt if alt else ident)
                teams.append(name)

            if len(teams) >= 2:
                matches.append((teams[0], teams[1]))

        browser.close()
    return matches

if __name__ == "__main__":
    # 1. vider le fichier dès le début
    open(OUTPUT_FILE, "w", encoding="utf-8").close()

    # 2. récupérer tous les matchs
    matches = fetch_matches()

    # 3. supprimer les doublons tout en conservant l'ordre
    seen, unique_matches = set(), []
    for t1, t2 in matches:
        key = (t1, t2)
        if key not in seen:
            seen.add(key)
            unique_matches.append(key)

    # 4. écrire les matchs uniques
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        for t1, t2 in unique_matches:
            f.write(f"{t1} vs {t2}\n")

    print(f"[OK] {len(unique_matches)} matchs uniques écrits dans {OUTPUT_FILE}")