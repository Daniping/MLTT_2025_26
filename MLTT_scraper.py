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

        # On attend que les noms apparaissent (souvent dans h3 ou h2)
        await page.wait_for_selector("h2, h3", timeout=20000)

        # On récupère tous les textes visibles
        raw_texts = await page.eval_on_selector_all(
            "h2, h3, div, span",
            "elements => elements.map(e => e.innerText.trim()).filter(t => t)"
        )

        await browser.close()

        # On filtre pour ne garder que les vrais noms d'équipes
        teams = [t for t in raw_texts if " " in t and len(t) < 40]  # heuristique simple
        return sorted(set(teams))


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