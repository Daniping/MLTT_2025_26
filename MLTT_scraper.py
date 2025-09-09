# ===========================================
# MLTT_extract_hexas.py
# - Récupère tous les Hexas des équipes visibles sur la page
# - Conserve le sélecteur de chaque équipe
# - Écrit dans hexas_teams.csv pour analyse
# ===========================================

from playwright.sync_api import sync_playwright
import csv

URL = "https://mltt.com/league/schedule"
OUTPUT_CSV = "hexas_teams.csv"

# Équipes connues pour comparaison
KNOWN_TEAMS = {
    "687762138fa2e035f9b328c8": "Princeton Revolution",
    "687762138fa2e035f9b328f1": "New York Slice",
    "687762138fa2e035f9b32901": "Carolina Gold Rush",
    "687762138fa2e035f9b32902": "Florida Crocs",
    "687762138fa2e035f9b32905": "Atlanta Blazers",
    "687762138fa2e035f9b32907": "Portland Paddlers",
    "687762138fa2e035f9b32909": "Texas Smash",
    "687762138fa2e035f9b3290b": "Los Angeles Spinners",
    "687762138fa2e035f9b3290d": "Bay Area Blasters",
    "687762138fa2e035f9b3290f": "Chicago Wind",
}

def extract_hexas():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL, timeout=60000)
        page.wait_for_timeout(5000)

        # Récupération de tous les logos d'équipes sur la page
        team_imgs = page.query_selector_all("div.schedule-team-logo img")
        hexas_list = []

        for img in team_imgs:
            alt = img.get_attribute("alt")
            src = img.get_attribute("src") or ""
            ident = src.split("/")[-1].split("_")[0] if src else "?"
            known_name = KNOWN_TEAMS.get(ident, "")
            hexas_list.append({
                "hexa": ident,
                "alt_text": alt,
                "known_name": known_name,
                "selector": "div.schedule-team-logo img"
            })

        browser.close()
        return hexas_list

if __name__ == "__main__":
    hexas = extract_hexas()
    # Sauvegarde dans CSV
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["hexa", "alt_text", "known_name", "selector"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in hexas:
            writer.writerow(row)

    print(f"[OK] {len(hexas)} entrées écrites dans {OUTPUT_CSV}")