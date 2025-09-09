# MLTT_team_hexas_v2.py
# Extraction plus robuste des identifiants hexadécimaux (logos / liens / styles)
from playwright.sync_api import sync_playwright
import re

URL = "https://mltt.com/league/schedule"
OUTPUT_FILE = "team_hexas.txt"
HEX_PATTERN = re.compile(r"([0-9a-f]{24})", re.IGNORECASE)

def fetch_team_hexas():
    hexes = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = browser.new_page()
        page.goto(URL, timeout=60000)
        # petit délai initial
        page.wait_for_timeout(2000)

        # scroller pour forcer le lazy-load
        for _ in range(10):
            page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
            page.wait_for_timeout(400)

        # récupérer un ensemble d'emplacements où un ID peut apparaître
        payload = page.evaluate("""() => {
            const imgs = Array.from(document.querySelectorAll('img')).map(i => (i.src || i.getAttribute('data-src') || ''));
            const attrs = [];
            // extraire attributes susceptibles de contenir des URLs (style, data-*, srcset...)
            Array.from(document.querySelectorAll('*')).forEach(el => {
                for (let a of el.attributes) {
                    if (a && a.value && typeof a.value === 'string') attrs.push(a.value);
                }
                if (el.srcset) attrs.push(el.srcset);
                if (el.style && el.style.backgroundImage) attrs.push(el.style.backgroundImage);
            });
            const hrefs = Array.from(document.querySelectorAll('a[href]')).map(a => a.getAttribute('href') || '');
            return {imgs, attrs, hrefs, imgs_count: document.querySelectorAll('img').length};
        }""")

        # Chercher les hexas dans tous les champs récupérés
        for s in payload.get("imgs", []) + payload.get("attrs", []) + payload.get("hrefs", []):
            if not s:
                continue
            for m in HEX_PATTERN.finditer(s):
                hexes.add(m.group(1))

        browser.close()

    return sorted(hexes)

if __name__ == "__main__":
    hexas = fetch_team_hexas()
    # écriture
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for h in hexas:
            f.write(h + "\n")

    print(f"[OK] {len(hexas)} identifiants extraits et sauvés dans {OUTPUT_FILE}")
    for h in hexas:
        print(h)