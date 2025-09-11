from playwright.sync_api import sync_playwright

OUTPUT_FILE = "MLTT_2025_26_V5.ics"

def fetch_schedule_matches(page):
    matches = []
    match_blocks = page.query_selector_all("div.future-match-single-top-wrap")
    for block in match_blocks:
        team_names = block.query_selector_all("h3.future-match-game-title")
        teams = [t.inner_text().strip() for t in team_names if t.inner_text().strip()]
        if len(teams) >= 2:
            matches.append((teams[0], teams[1]))
    return matches

def fetch_team_names(page):
    teams = set()
    team_blocks = page.query_selector_all("div.team-block")  # ajuster selon structure réelle
    for block in team_blocks:
        name_el = block.query_selector("h3.team-name")  # ou "div.team-name" selon site
        if name_el:
            name = name_el.inner_text().strip()
            if name:
                teams.add(name)
    return teams

if __name__ == "__main__":
    open(OUTPUT_FILE, "w", encoding="utf-8").close()  # vider fichier

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # 1. récupérer tous les matchs
        page.goto("https://mltt.com/league/schedule", timeout=60000)
        page.wait_for_timeout(5000)
        matches = fetch_schedule_matches(page)

        # 2. récupérer toutes les équipes connues depuis /teams
        page.goto("https://mltt.com/teams", timeout=60000)
        page.wait_for_timeout(5000)
        teams_from_page = fetch_team_names(page)

        browser.close()

    # 3. compléter les équipes manquantes dans les matchs
    all_matches = []
    for t1, t2 in matches:
        all_matches.append((t1, t2))
        # Optionnel: vérifier si t1 ou t2 ne sont pas dans teams_from_page et ajuster

    # 4. supprimer doublons
    seen, unique_matches = set(), []
    for t1, t2 in all_matches:
        key = (t1, t2)
        if key not in seen:
            seen.add(key)
            unique_matches.append(key)

    # 5. écrire les matchs uniques en clair
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        for t1, t2 in unique_matches:
            f.write(f"{t1} vs {t2}\n")

    print(f"[OK] {len(unique_matches)} matchs uniques écrits dans {OUTPUT_FILE}")