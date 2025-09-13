import asyncio
import re
import requests
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

OUTPUT_FILE = "MLTT_2025_26_V5.ics"

async def main():
    # 1) Scraper les équipes
    teams_url = "https://mltt.com/teams"
    r = requests.get(teams_url)
    soup = BeautifulSoup(r.text, "html.parser")

    team_mapping = {}
    for img in soup.find_all("img", alt=True, src=True):
        alt = img["alt"].strip()
        src = img["src"]
        m = re.search(r"([0-9a-f]{24})", src)
        if alt and m:
            team_mapping[m.group(1)] = alt

    # 2) Scraper les matchs
    schedule_url = "https://mltt.com/league/schedule"
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(schedule_url)
        await page.wait_for_selector("div.schedule-card")  # chaque match

        matches = await page.query_selector_all("div.schedule-card")
        lines = []

        for match in matches:
            date = await match.query_selector_eval(".date", "el => el.textContent") if await match.query_selector(".date") else "?"
            time = await match.query_selector_eval(".time", "el => el.textContent") if await match.query_selector(".time") else "?"
            location = await match.query_selector_eval(".location", "el => el.textContent") if await match.query_selector(".location") else "?"

            imgs = await match.query_selector_all("img")
            teams = []
            for img in imgs:
                src = await img.get_attribute("src")
                if src:
                    m = re.search(r"([0-9a-f]{24})", src)
                    if m:
                        teams.append(team_mapping.get(m.group(1), "?"))

            if len(teams) == 2:
                line = f"{date} {time} – {teams[0]} vs {teams[1]} – {location}"
                if "Sep" in date:
                    lines.append(line)

        await browser.close()

    # 3) Sauvegarde dans le repo
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("Matchs MLTT – Septembre 2025\n\n")
        for line in lines:
            f.write(line + "\n")

    print(f"{len(lines)} matchs écrits dans {OUTPUT_FILE}")

if __name__ == "__main__":
    asyncio.run(main())