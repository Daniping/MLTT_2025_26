# ===========================================
# MLTT_scraper.py - Minimalist final version
# - Vide le fichier dès le début
# - Récupère les noms d'équipes depuis /teams
# - Récupère les matchs depuis /league/schedule
# - Supprime les doublons
# - Écrit dans MLTT_2025_26_V5.ics
# ===========================================

from playwright.sync_api import sync_playwright

OUTPUT_FILE = "MLTT_2025_26_V5.ics"

def fetch_teams():
    url = "https://mltt.com/teams"
    teams = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)
        page.wait_for_timeout(5000)
        
        team_elements = page.query_selector_all("div.team-card h3, div.team-card .team-name")
        for el in team_elements:
            text = el.inner_text().strip()
            if text:
                teams.append(text)
        
        browser.close()
    return list(dict.fromkeys(teams))  # supprimer doublons tout en conservant l'ordre

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
            imgs = block.query_selector_all("div.schedule-team-logo img")
            teams = []
            for img in imgs:
                alt = img.get_attribute("alt")
                src = img.get_attribute("src") or ""
                name = alt if alt else src.split("/")[-1].split("_")[0]
                teams.append(name)
            if len(teams) >= 2:
                matches.append((teams[0], teams[1]))
        
        browser.close()
    return matches

if __name__ == "__main__":
    # 1. Vider le fichier dès le départ
    open(OUTPUT_FILE, "w", encoding="utf-8").close()
    
    # 2. Récupérer toutes les équipes
    teams = fetch_teams()
    
    # 3. Récupérer tous les matchs
    matches = fetch_matches()
    
    # 4. Supprimer doublons
    seen = set()
    unique_matches = []
    for t1, t2 in matches:
        key = (t1, t2)
        if key not in seen:
            seen.add(key)
            unique_matches.append(key)
    
    # 5. Écrire dans le fichier
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        f.write("\n".join(teams) + "\n\n")
        for t1, t2 in unique_matches:
            f.write(f"{t1} vs {t2}\n")
    
    print(f"[OK] {len(teams)} équipes et {len(unique_matches)} matchs écrits dans {OUTPUT_FILE}")