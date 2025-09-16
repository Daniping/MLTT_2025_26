# ===========================================
# MLTT_debug.py - Debug extraction
# - Liste tous les <img> src et alt
# - Liste tous les titres <h2> et <h3>
# ===========================================

from playwright.sync_api import sync_playwright

OUTPUT_FILE = "MLTT_2025_26_V5.ics"

def debug_page():
    url = "https://mltt.com/teams"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)
        page.wait_for_timeout(5000)

        imgs = page.query_selector_all("img")
        titles = page.query_selector_all("h2, h3")

        results = []

        results.append("=== IMAGES ===")
        for img in imgs:
            src = img.get_attribute("src")
            alt = img.get_attribute("alt")
            results.append(f"src={src} | alt={alt}")

        results.append("\n=== TITLES ===")
        for t in titles:
            txt = t.inner_text().strip()
            results.append(txt)

        browser.close()
    return results


if __name__ == "__main__":
    # 1. vider le fichier dès le début
    open(OUTPUT_FILE, "w", encoding="utf-8").close()

    # 2. récupérer debug infos
    data = debug_page()

    # 3. écrire dans le fichier
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        for line in data:
            f.write(line + "\n")

    print(f"[OK] {len(data)} lignes écrites dans {OUTPUT_FILE}")