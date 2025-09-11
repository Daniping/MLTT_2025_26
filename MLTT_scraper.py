# MLTT_scraper.py
import asyncio
from playwright.async_api import async_playwright

ICS_FILE = "MLTT_2025_26_V5.ics"
TEAMS_URL = "https://mltt.com/teams"


async def scrape_teams():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(TEAMS_URL, timeout=60000)

        # On attend que les logos apparaissent (sélecteur robuste)
        await page.wait_for_selector("img[alt]", timeout=20000)

        # On récupère les noms d'équipes
        teams = await page.eval_on_selector_all(
            "img[alt]", "elements => elements.map(e => e.alt.trim()).filter(t => t)"
        )

        await browser.close()
        return sorted(set(teams))  # unique + tri


def write_ics(teams):
    # On efface et recrée le fichier ICS
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