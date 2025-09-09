# ===========================================
# MLTT_scraper.py - Scraper MLTT minimal
# Écrit directement les matchs en clair dans MLTT_2025_26_V5.ics
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
                alt = img.get_attribute("alt")
                src = img.get_attribute("src")
                # On prend alt si présent, sinon l'identifiant du logo
                teams.append(alt if alt else src.split("/")[-1].split("_")[0])

            team1 = teams[0] if len(teams) > 0 else "?"
            team2 = teams[1] if len(teams) > 1 else "?"
            matches.append({"team1": team1, "team2": team2})

        browser.close()

    return matches

if __name__ == "__main__":
    matches = fetch_matches()

    # Écriture directe dans le fichier du repo, mode append
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        for match in matches:
            f.write(f"{match['team1']} vs {match['team2']}\n")

    print(f"[OK] {len(matches)} matchs ajoutés dans {OUTPUT_FILE}")