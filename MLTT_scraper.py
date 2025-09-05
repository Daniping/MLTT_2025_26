# ===========================================
# MLTT_scraper.py - Version ICS lisible
# Objectif : Charger la page MLTT avec Playwright,
# récupérer les matchs et les écrire dans le fichier
# MLTT_2025_26_V5.ics existant en clair
# ===========================================

from playwright.sync_api import sync_playwright
from datetime import datetime
import os

OUTPUT_ICS = "MLTT_2025_26_V5.ics"

# Mapping pour remplacer les identifiants des logos par les vrais noms
TEAM_MAPPING = {
    "687762138fa2e035f9b328c8_PRIMARY-BLACK-OUTLINE": "Princeton Revolution",
    "687762138fa2e035f9b328f1_PRIMARY-BLACK-OUTLINE": "New York Slice",
    "687762138fa2e035f9b32901_PRIMARY-WHITE-OUTLINE": "Carolina Gold Rush",
    "687762138fa2e035f9b32902_PRIMARY-BLACK-OUTLINE": "Florida Crocs",
    "687762138fa2e035f9b32905_PRIMARY-LOCKUP": "Atlanta Blazers",
    "687762138fa2e035f9b32a0f_AltLogo": "Portland Paddlers",
    "685e2c34b9486ae92f5afa74_PRIMARY-BLACK-OUTLINE": "Texas Smash",
    "687762138fa2e035f9b329c6_wind": "Bay Area Blasters",
    "687762138fa2e035f9b329c5_SPINNERS": "Los Angeles Spinners",
    "687762138fa2e035f9b328f2_PRIMARY-WHITE-OUTLINE": "Chicago Wind"
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
            # Date
            date_el = block.query_selector("h3.future-match-game-title")
            date_text = date_el.inner_text().strip() if date_el else "?"
            try:
                date_obj = datetime.strptime(date_text, "%b %d, %Y %I:%M %p")
            except Exception:
                date_obj = None

            # Lieu
            venue_el = block.query_selector("h3.city-state")
            venue = venue_el.inner_text().strip() if venue_el else "?"

            # Équipes
            team_imgs = block.query_selector_all("div.schedule-team-logo img")
            teams = []
            for img in team_imgs:
                src = img.get_attribute("src")
                base = os.path.basename(src).split(".")[0]
                name = TEAM_MAPPING.get(base, base)
                teams.append(name)

            team1 = teams[0] if len(teams) > 0 else "?"
            team2 = teams[1] if len(teams) > 1 else "?"

            # Ticket link
            ticket_el = block.query_selector("a.primary-btn-link-wrap")
            ticket = ticket_el.get_attribute("href") if ticket_el else None

            matches.append({
                "team1": team1,
                "team2": team2,
                "date": date_obj.isoformat() if date_obj else date_text,
                "venue": venue,
                "ticket": ticket
            })

        browser.close()

    return matches

def write_ics(matches):
    with open(OUTPUT_ICS, "w", encoding="utf-8") as f:
        f.write("BEGIN:VCALENDAR\n")
        for m in matches:
            f.write(f"SUMMARY:{m['team1']} vs {m['team2']}\n")
            f.write(f"DTSTART:{m['date']}\n")
            f.write(f"LOCATION:{m['venue']}\n")
            if m.get("ticket"):
                f.write(f"URL:{m['ticket']}\n")
            f.write("\n")
        f.write("END:VCALENDAR\n")
    print(f"[OK] Données sauvegardées dans {OUTPUT_ICS}")

if __name__ == "__main__":
    matches = fetch_matches()
    print(f"[OK] Nombre de matchs trouvés: {len(matches)}")
    for m in matches[:5]:
        print(m)
    write_ics(matches)