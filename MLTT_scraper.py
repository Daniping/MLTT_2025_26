# MLTT_scraper.py - Match teams only, append to ICS

from playwright.sync_api import sync_playwright
import os

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
                teams.append(alt if alt else os.path.basename(src).split("_")[0])

            team1 = teams[0] if len(teams) > 0 else "?"
            team2 = teams[1] if len(teams) > 1 else "?"
            matches.append(f"{team1} vs {team2}")

        browser.close()

    return matches

if __name__ == "__main__":
    matches = fetch_matches()
    print(f"[OK] Nombre de matchs trouvés: {len(matches)}")

    # Append matches to the ICS file
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        for m in matches:
            f.write(m + "\n")

    print(f"[OK] Matchs ajoutés dans {OUTPUT_FILE}")