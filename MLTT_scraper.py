from playwright.sync_api import sync_playwright

OUTPUT_FILE = "MLTT_2025_26_V5.ics"

# 1️⃣ Vider le fichier au tout début
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    pass  # juste pour effacer tout le contenu

# 2️⃣ Fonction de scraping
def fetch_matches():
    url = "https://mltt.com/league/schedule"
    matches = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)
        page.wait_for_timeout(5000)

        match_blocks = page.query_selector_all("div.future-match-single-top-wrap")
        for block in match_blocks:
            team_imgs = block.query_selector_all("div.schedule-team-logo img")
            teams = []
            for img in team_imgs:
                alt = img.get_attribute("alt")
                src = img.get_attribute("src")
                teams.append(alt if alt else src.split("/")[-1].split("_")[0])
            
            team1 = teams[0] if len(teams) > 0 else "?"
            team2 = teams[1] if len(teams) > 1 else "?"
            matches.append({"team1": team1, "team2": team2})

        browser.close()
    return matches

# 3️⃣ Conversion Hexa → nom pour les 3 équipes et suppression des doublons
TEAM_MAPPING = {
    "687762138fa2e035f9b328c8": "Princeton Revolution",
    "687762138fa2e035f9b328f1": "New York Slice",
    "687762138fa2e035f9b32902": "Carolina Gold Rush"
}

if __name__ == "__main__":
    matches = fetch_matches()

    # garder seulement uniques
    seen = set()
    unique_matches = []
    for m in matches:
        t1 = TEAM_MAPPING.get(m['team1'], m['team1'])
        t2 = TEAM_MAPPING.get(m['team2'], m['team2'])
        line = f"{t1} vs {t2}"
        if line not in seen:
            seen.add(line)
            unique_matches.append(line)

    # 4️⃣ Écriture finale dans le fichier vidé au départ
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        for line in unique_matches:
            f.write(line + "\n")

    print(f"[OK] {len(unique_matches)} matchs écrits dans {OUTPUT_FILE}")