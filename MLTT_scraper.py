from playwright.sync_api import sync_playwright

# Fichier de sortie (non utilisé pour l’instant)
OUTPUT_FILE = "MLTT_2025_26_V5.ics"

# Dictionnaire complet des équipes (codes → noms)
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

def scrape_matches():
    matches = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://mltt.com/league/schedule")  # URL du calendrier MLTT

        # Sélecteur à adapter si besoin
        games = page.query_selector_all(".schedule-game")
        for game in games:
            try:
                team1 = game.get_attribute("data-team1")
                team2 = game.get_attribute("data-team2")
                date = game.get_attribute("data-date")
                venue = game.get_attribute("data-venue")

                matches.append({
                    "team1": team1,
                    "team2": team2,
                    "date": date,
                    "venue": venue
                })
            except Exception:
                continue

        browser.close()
    return matches

if __name__ == "__main__":
    matches = scrape_matches()
    print(f"[OK] Nombre de matchs trouvés: {len(matches)}")

    for match in matches:
        team1 = TEAM_MAP.get(match["team1"], match["team1"])
        team2 = TEAM_MAP.get(match["team2"], match["team2"])
        date = match["date"]
        venue = match["venue"]

        print(f"{team1} vs {team2} - Date: {date} - Lieu: {venue}")