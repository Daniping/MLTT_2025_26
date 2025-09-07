# ===========================================
# MLTT_scraper.py - Scrape Week 1 Matches
# Objectif : Récupérer les matchs Week 1 et écrire
# dans MLTT_2025_26_V5.ics en clair
# ===========================================

from playwright.sync_api import sync_playwright
from datetime import datetime
import os

# -----------------------------
# Fichier de sortie
# -----------------------------
OUTPUT_FILE = "MLTT_2025_26_V5.ics"

# -----------------------------
# Fonction pour récupérer les matchs
# -----------------------------
def fetch_week1_matches():
    url = "https://mltt.com/league/schedule"
    matches = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)
        page.wait_for_timeout(5000)  # attendre que JS charge tout

        # On récupère tous les blocs de matchs futurs
        match_blocks = page.query_selector_all("div.future-match-single-top-wrap")

        for block in match_blocks:
            # Filtrage pour Week 1 uniquement
            week_el = block.query_selector("div.schedule-week")
            week_text = week_el.inner_text().strip() if week_el else ""
            if "Week 1" not in week_text:
                continue

            # Équipes
            team_imgs = block.query_selector_all("div.schedule-team-logo img")
            teams = []
            for img in team_imgs:
                alt = img.get_attribute("alt")
                src = img.get_attribute("src")
                # on prend l'alt si existant, sinon le nom codé dans src
                teams.append(alt if alt else os.path.basename(src).split("_")[0])

            team1 = teams[0] if len(teams) > 0 else "?"
            team2 = teams[1] if len(teams) > 1 else "?"

            # Date & heure
            date_el = block.query_selector("h3.future-match-game-title")
            date_text = date_el.inner_text().strip() if date_el else "?"
            try:
                date_obj = datetime.strptime(date_text, "%b %d, %Y %I:%M %p")
                date_str = date_obj.strftime("%Y-%m-%d")
                time_str = date_obj.strftime("%H:%M")
            except Exception:
                date_str, time_str = date_text, "?"

            # Lieu
            venue_el = block.query_selector("h3.city-state")
            venue = venue_el.inner_text().strip() if venue_el else "?"

            matches.append({
                "team1": team1,
                "team2": team2,
                "date": date_str,
                "time": time_str,
                "venue": venue
            })

        browser.close()

    return matches

# -----------------------------
# Écriture des matchs dans le fichier
# -----------------------------
def save_matches(matches):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:  # "w" pour vider le fichier avant
        for m in matches:
            line = f"{m['team1']} vs {m['team2']} - Date: {m['date']}, Heure: {m['time']}, Lieu: {m['venue']}\n\n"
            f.write(line)
    print(f"[OK] {len(matches)} matchs écrits dans {OUTPUT_FILE}")

# -----------------------------
# Main
# -----------------------------
if __name__ == "__main__":
    matches = fetch_week1_matches()
    print(f"[OK] Nombre de matchs Week 1 trouvés: {len(matches)}")
    for m in matches:
        print(f"{m['team1']} vs {m['team2']}")
    save_matches(matches)