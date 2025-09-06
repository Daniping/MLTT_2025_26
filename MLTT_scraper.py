# ===========================================
# MLTT_scraper.py - Version 4.1
# Objectif : Récupérer les matchs MLTT, 
# les écrire en clair dans MLTT_2025_26_V5.ics
# ===========================================

from playwright.sync_api import sync_playwright
from datetime import datetime
import os

OUTPUT_ICS = "MLTT_2025_26_V5.ics"

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
            date_el = block.query_selector("h3.future-match-game-title")
            date_text = date_el.inner_text().strip() if date_el else "?"

            try:
                date_obj = datetime.strptime(date_text, "%b %d, %Y %I:%M %p")
                date_iso = date_obj.isoformat()
            except Exception:
                date_iso = date_text

            venue_el = block.query_selector("h3.city-state")
            venue = venue_el.inner_text().strip() if venue_el else "?"

            team_imgs = block.query_selector_all("div.schedule-team-logo img")
            teams = []
            for img in team_imgs:
                alt = img.get_attribute("alt")
                src = img.get_attribute("src")
                teams.append(alt if alt else os.path.basename(src).split("_")[0])

            team1 = teams[0] if len(teams) > 0 else "?"
            team2 = teams[1] if len(teams) > 1 else "?"

            matches.append({
                "team1": team1,
                "team2": team2,
                "date": date_iso,
                "venue": venue
            })

        browser.close()
    return matches

def save_matches_to_ics(matches):
    with open(OUTPUT_ICS, "w", encoding="utf-8") as f:
        f.write("BEGIN:MLTT_SCHEDULE\n")
        for m in matches:
            f.write(f"{m['date']} | {m['team1']} vs {m['team2']} | {m['venue']}\n")
        f.write("END:MLTT_SCHEDULE\n")
    print(f"[OK] Données sauvegardées dans {OUTPUT_ICS}")

if __name__ == "__main__":
    matches = fetch_matches()
    print(f"[OK] Nombre de matchs trouvés: {len(matches)}")
    for m in matches[:5]:
        print(m)
    save_matches_to_ics(matches)  # <-- Parenthèse fermée correctement