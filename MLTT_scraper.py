# ===========================================
# MLTT_team_names.py - Extraire les noms des équipes
# ===========================================

from playwright.sync_api import sync_playwright

URL = "https://mltt.com/league/schedule"  # ou la page Teams si différente

# Sélecteurs possibles pour le texte des équipes
TEAM_SELECTORS = [
    "h3",
    "h2",
    "div.team-name",
    "span.team-name",
    "div.schedule-team-logo img",  # fallback pour alt
]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(URL, timeout=60000)
    page.wait_for_timeout(5000)  # attendre le JS

    found_names = set()

    for selector in TEAM_SELECTORS:
        elements = page.query_selector_all(selector)
        for el in elements:
            text = el.inner_text() if hasattr(el, "inner_text") else el.get_attribute("alt")
            if text:
                found_names.add(text.strip())

    browser.close()

print("[OK] Équipes détectées :")
for name in sorted(found_names):
    print(name)