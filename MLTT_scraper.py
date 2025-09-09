import os
import json
from playwright.sync_api import sync_playwright

# Dossier de sortie (pour test, affichage dans le run)
OUTPUT_FILE = "MLTT_matches_test.txt"

TEAM_MAPPING = {
    # Ici tu peux mettre le mapping Hexa -> nom si nécessaire,
    # mais pour l'affichage, on prendra directement le code Hexa
}

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://mltt.com/league/schedule")

    # attend que le calendrier charge
    page.wait_for_selector("div.schedule-block")

    matches = []

    # récupérer tous les blocs de matchs
    schedule_blocks = page.query_selector_all("div.schedule-block")
    for block in schedule_blocks:
        # récupérer les logos (identifiants Hexa)
        team_imgs = block.query_selector_all("div.schedule-team-logo img")
        teams = []
        for img in team_imgs:
            src = img.get_attribute("src")
            base = os.path.basename(src).split(".")[0]
            base = base.replace("%20", "").split("(")[0].strip()
            teams.append(base)  # ici on garde le code Hexa

        # récupérer la date et le lieu si dispo
        date_elem = block.query_selector("div.schedule-date")
        venue_elem = block.query_selector("div.schedule-venue")
        date = date_elem.inner_text() if date_elem else "?"
        venue = venue_elem.inner_text() if venue_elem else "?"

        if len(teams) == 2:
            match = {
                "team1": teams[0],
                "team2": teams[1],
                "date": date,
                "venue": venue
            }
            matches.append(match)

    browser.close()

# Affichage clair dans le run
print(f"[OK] Nombre de matchs trouvés: {len(matches)}")
for m in matches:
    print(m)

# Sauvegarde dans un fichier test pour vérification
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    for m in matches:
        f.write(f"{m['team1']} vs {m['team2']} - Date: {m['date']}, Lieu: {m['venue']}\n\n")

print(f"[OK] Données sauvegardées dans {OUTPUT_FILE}")