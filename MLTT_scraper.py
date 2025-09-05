# ===========================================
# MLTT_scraper.py
# Objectif : Scraper la page MLTT, récupérer les matchs
# et écrire les résultats directement dans
# MLTT_2025_26_V5.ICS en clair
# ===========================================

from playwright.sync_api import sync_playwright
from datetime import datetime
import os

OUTPUT_FILE = "MLTT_2025_26_V5.ICS"

def fetch_matches():
    url = "https://mltt.com/league/schedule"
    matches = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)
        page.wait_for_timeout(5000)  # attendre que JS charge tout

        # Récupération des blocs de matchs
        match_blocks = page.query_selector_all("div.future-match-single-top-wrap")

        for block in match_blocks:
            # Date
            date_el = block.query_selector("h3.future-match-game-title")
            date_text = date_el.inner_text().strip() if date_el else "?"
            try:
                date_obj = datetime.strptime(date_text, "%b %d, %Y %I:%M %p")
                date_iso = date_obj.isoformat()
            except Exception:
                date_iso = date_text

            # Lieu
            venue_el = block.query_selector("h3.city-state")
            venue = venue_el.inner_text().strip() if venue_el else "?"

            # Équipes (à partir du nom du fichier ou alt)
            team_imgs = block.query_selector_all("div.schedule-team-logo img")
            teams = []
            for img in team_imgs:
                alt = img.get_attribute("alt")
                src = img.get_attribute("src")
                # on prend alt si disponible sinon nom du fichier
                team_name = alt if alt else os.path.basename(src).split("_")[0]
                teams.append(team_name)

            team1 = teams[0] if len(teams) > 0 else "?"
            team2 = teams[1] if len(teams) > 1 else "?"

            # Ticket link
            ticket_el = block.query_selector("a.primary-btn-link-wrap")
            ticket = ticket_el.get_attribute("href") if ticket_el else "?"

            matches.append({
                "team1": team1,
                "team2": team2,
                "date": date_iso,
                "venue": venue,
                "ticket": ticket
            })

        browser.close()
    return matches

if __name__ == "__main__":
    matches = fetch_matches()
    print(f"[OK] Nombre de matchs trouvés: {len(matches)}")

    # Écriture en clair dans MLTT_2025_26_V5.ICS
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for m in matches:
            line = f"{m['team1']} vs {m['team2']} | {m['date']} | {m['venue']} | {m['ticket']}\n"
            f.write(line)
            print(line.strip())

    print(f"[OK] Données sauvegardées dans {OUTPUT_FILE}")