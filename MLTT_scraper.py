# ===========================================
# MLTT_team_hexas.py - Extraction brute des identifiants d'équipes
# ===========================================

from playwright.sync_api import sync_playwright

OUTPUT_FILE = "team_hexas.txt"

def fetch_team_hexas():
    url = "https://mltt.com/league/schedule"
    hexas = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)
        page.wait_for_timeout(5000)

        # Cherche tous les logos d'équipes
        team_imgs = page.query_selector_all("div.schedule-team-logo img")
        for img in team_imgs:
            src = img.get_attribute("src") or ""
            ident = src.split("/")[-1].split("_")[0] if src else "?"
            hexas.add(ident)

        browser.close()

    return sorted(hexas)

if __name__ == "__main__":
    hexas = fetch_team_hexas()

    # Écriture dans un fichier texte
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for h in hexas:
            f.write(h + "\n")

    print(f"[OK] {len(hexas)} identifiants extraits :")
    for h in hexas:
        print(h)
    print(f"[OK] Également sauvegardés dans {OUTPUT_FILE}")