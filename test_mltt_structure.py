import requests
from bs4 import BeautifulSoup

MLTT_URL = "https://www.mltt.com/league/schedule"

print(f"🔍 Lecture de la page : {MLTT_URL}")
r = requests.get(MLTT_URL)
r.raise_for_status()
soup = BeautifulSoup(r.text, "html.parser")
print("✅ Page téléchargée avec succès.\n")

# Affiche toutes les balises <h3> et leurs suivantes (quelques lignes)
for h3 in soup.find_all("h3"):
    print("=== H3 ===")
    print(h3.get_text(strip=True))
    
    # Affiche les 3 balises suivantes après chaque <h3>
    sibling = h3.find_next_sibling()
    count = 0
    while sibling and count < 3:
        print(f"> {sibling.name} : {sibling.get_text(strip=True)[:100]}")  # premiers 100 caractères
        sibling = sibling.find_next_sibling()
        count += 1
    print("\n")
