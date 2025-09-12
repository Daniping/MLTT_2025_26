import asyncio
import uuid
from datetime import datetime
from playwright.async_api import async_playwright

TEAMS_URL = "https://mltt.com/teams"
SCHEDULE_URL = "https://mltt.com/league/schedule"
ICS_FILE = "MLTT_2025_26_V5.ics"

async def scrape():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # --- 1. Récupérer les équipes (logo -> nom)
        await page.goto(TEAMS_URL, timeout=60000)
        await page.wait_for_selector("img")
        logos = await page.query_selector_all("img")

        logo_to_name = {}
        for img in logos:
            src = await img.get_attribute("src")
            alt = await img.get_attribute("alt")
            if src and alt:
                if "PRIMARY" in src or "LOCKUP" in src:  # logos d'équipes
                    key = src.split("/")[-1].split("_")[0]  # ex: 687762138fa2e035f9b328f1
                    logo_to_name[key] = alt.strip()

        print("Équipes trouvées :", logo_to_name)

        # --- 2. Récupérer les matchs
        await page.goto(SCHEDULE_URL, timeout=60000)
        await page.wait_for_selector(".future-match-single-top-wrap")

        matches = []
        blocks = await page.query_selector_all(".future-match-single-top-wrap")
        for block in blocks:
            imgs = await block.query_selector_all("img.future-match-single-clab-logo")
            if len(imgs) == 2:
                team_keys = []
                for img in imgs:
                    src = await img.get_attribute("src")
                    if src:
                        team_keys.append(src.split("/")[-1].split("_")[0])
                if len(team_keys) == 2:
                    # Date et heure
                    date_el = await block.query_selector("h3.future-match-game-title")
                    date_txt = await date_el.inner_text() if date_el else None
                    matches.append((team_keys[0], team_keys[1], date_txt))

        await browser.close()

        # --- 3. Écrire ICS
        with open(ICS_FILE, "w", encoding="utf-8") as f:
            f.write("BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//MLTT//Schedule 2025-26//EN\n")
            for team1, team2, date_txt in matches:
                name1 = logo_to_name.get(team1, team1)
                name2 = logo_to_name.get(team2, team2)
                summary = f"{name1} vs {name2}"

                # UID unique
                uid = f"{uuid.uuid4()}@mltt.com"

                # Date ICS si dispo
                dtstamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
                dtstart = "20250901T000000Z"  # placeholder tant qu’on ne parse pas les vraies dates

                f.write("BEGIN:VEVENT\n")
                f.write(f"UID:{uid}\n")
                f.write(f"DTSTAMP:{dtstamp}\n")
                f.write(f"DTSTART:{dtstart}\n")
                f.write(f"SUMMARY:{summary}\n")
                f.write("END:VEVENT\n")

            f.write("END:VCALENDAR\n")

if __name__ == "__main__":
    asyncio.run(scrape())