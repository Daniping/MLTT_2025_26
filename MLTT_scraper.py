from playwright.sync_api import sync_playwright
from datetime import datetime

OUTPUT_FILE = "MLTT_2025_26"  # fichier texte clair

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
            # Date
            date_el = block.query_selector("h3.future-match-game-title")
            date_text = date_el.inner_text().strip() if date_el else "?"
            try:
                date_obj = datetime.strptime(date_text, "%b %d, %Y %I:%M %p")
                date_val = date_obj.isoformat()
            except Exception:
                date_val = date_text

            # Lieu
            venue_el = block.query_selector("h3.city-state")
            venue = venue_el.inner_text().strip() if venue_el else "?"

            # Équipes
            team_imgs = block.query_selector_all("div.schedule-team-logo img")
            teams = []
            for img in team_imgs:
                alt = img.get_attribute("alt")
                src = img.get_attribute("src")
                base = src.split("/")[-1].split("_")[0] if src else "?"
                teams.append(alt if alt else base)

            team1 = teams[0] if len(teams) > 0 else "?"
            team2 = teams[1] if len(teams) > 1 else "?"

            # Ticket
            ticket_el = block.query_selector("a.primary-btn-link-wrap")
            ticket = ticket_el.get_attribute("href") if ticket_el else None

            matches.append(f"{date_val} | {team1} vs {team2} @ {venue} | Ticket: {ticket}")

        browser.close()

    return matches

if __name__ == "__main__":
    matches = fetch_matches()
    print(f"[OK] Nombre de matchs trouvés: {len(matches)}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for line in matches:
            f.write(line + "\n")

    print(f"[OK] Données sauvegardées dans {OUTPUT_FILE}")