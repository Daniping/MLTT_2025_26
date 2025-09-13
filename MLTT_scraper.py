from playwright.sync_api import sync_playwright

OUTPUT_FILE = "MLTT_2025_26_V5.ics"

def fetch_team_names():
    url = "https://mltt.com/teams"
    names = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)
        page.wait_for_timeout(5000)
        team_elements = page.query_selector_all("div.team-card h3")  # récupère le nom affiché
        for el in team_elements:
            name = el.inner_text().strip()
            if name:
                names.append(name)
        browser.close()
    return names

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
            team_elements = block.query_selector_all("div.future-match-single-clab-details h3")  # texte des équipes
            if len(team_elements) >= 2:
                t1 = team_elements[0].inner_text().strip()
                t2 = team_elements[1].inner_text().strip()
                matches.append((t1, t2))
        browser.close()
    return matches

if __name__ == "__main__":
    open(OUTPUT_FILE, "w", encoding="utf-8").close()  # vide le fichier

    matches = fetch_matches()

    # supprimer les doublons
    seen, unique_matches = set(), []
    for t1, t2 in matches:
        key = (t1, t2)
        if key not in seen:
            seen.add(key)
            unique_matches.append(key)

    # écrire dans le fichier .ics
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        for t1, t2 in unique_matches:
            f.write(f"{t1} vs {t2}\n")

    print(f"[OK] {len(unique_matches)} matchs uniques écrits dans {OUTPUT_FILE}")