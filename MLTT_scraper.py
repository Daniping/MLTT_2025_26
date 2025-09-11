# MLTT_scraper.py
import asyncio
from playwright.async_api import async_playwright
import re

ICS_FILE = "MLTT_2025_26_V5.ics"
TEAMS_URL = "https://mltt.com/teams"


async def scrape_teams():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(TEAMS_URL, timeout=60000)

        # attendre que la page charge
        await page.wait_for_selector("body", timeout=20000)

        # récupérer tous les textes visibles
        raw_texts = await page.eval_on_selector_all(
            "h1, h2, h3, div, span",
            "els => els.map(e => e.innerText.trim()).filter(t => t)"
        )
        await browser.close()

        # filtrer : on garde uniquement les noms d’équipes (heuristique stricte)
        candidates = []
        for t in raw_texts:
            if len(t) < 30 and re.match(r"^[A-Za-z ]+$", t):  # uniquement lettres et espaces
                if " " in t:  # doit contenir au moins deux mots
                    candidates.append(t.strip())

        # dédoublonner sans tenir compte de la casse
        unique = []
        seen = set()
        for t in candidates:
            key = t.lower()
            if key not in seen:
                seen.add(key)
                unique.append(t)

        return unique


def write_ics(teams):
    with open(ICS_FILE, "w", encoding="utf-8") as f:
        f.write("BEGIN:VCALENDAR\n")
        f.write("VERSION:2.0\n")
        f.write("PRODID:-//MLTT Scraper//EN\n")

        for idx, team in enumerate(teams, start=1):
            f.write("BEGIN:VEVENT\n")
            f.write(f"UID:{idx}@mltt.com\n")
            f.write(f"SUMMARY:{team}\n")
            f.write("END:VEVENT\n")

        f.write("END:VCALENDAR\n")


async def main():
    teams = await scrape_teams()
    print("[OK] Équipes détectées :")
    for t in teams:
        print("-", t)

    write_ics(teams)
    print(f"[OK] Fichier {ICS_FILE} mis à jour avec {len(teams)} équipes.")


if __name__ == "__main__":
    asyncio.run(main())