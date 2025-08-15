import requests
from bs4 import BeautifulSoup

MLTT_URL = "https://www.mltt.com/league/schedule"

r = requests.get(MLTT_URL)
r.raise_for_status()
soup = BeautifulSoup(r.text, "html.parser")

# Sélecteur pour les matchs : <h3> suivi de div.match
matches = soup.select("h3 + div.match")

print(f"🔍 Nombre de matchs trouvés : {len(matches)}\n")

# Affiche le HTML des 5 premiers matchs pour vérifier la structure
for i, match in enumerate(matches[:5], 1):
    print(f"--- Match {i} ---")
    title = match.find_previous("h3").get_text(strip=True)
    print(f"Titre : {title}")
    print("HTML du match :")
    print(match.prettify())
    print("\n")
