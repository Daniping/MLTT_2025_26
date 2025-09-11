# scraper_hexas.py
from playwright.sync_api import sync_playwright
import re

OUTPUT_FILE = "team_hexas.txt"
TEAMS_URL = "https://mltt.com/league/teams"

def main():
    # Écrase le fichier au début
    open(OUTPUT_FILE, "w").close()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(TEAMS_URL, wait_until="networkidle")

        # Récupère tous les <img> présents sur la page
        imgs = page.query_selector_all("img")

        hexas = set()
        for img in imgs:
            src = img.get_attribute("src") or ""
            match = re.search(r"/([0-9a-f]{24})/", src)
            if match:
                hexas.add(match.group(1))

        browser.close()

    # Écriture finale triée
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for h in sorted(hexas):
            f.write(h + "\n")

    print(f"[OK] {len(hexas)} identifiants uniques extraits → {OUTPUT_FILE}")

if __name__ == "__main__":
    main()