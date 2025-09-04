import requests
from bs4 import BeautifulSoup
from datetime import datetime

URL = "https://mltt.com/league/schedule"

# Récupération de la page
resp = requests.get(URL)
resp.raise_for_status()
soup = BeautifulSoup(resp.text, "html.parser")

# Récupérer les équipes
teams = []
for item in soup.select("div.w-dyn-item a.pages-link div"):
    teams.append(item.get_text(strip=True))
print(f"[OK] Équipes récupérées ({len(teams)}): {teams}")

# Récupérer les matchs
matches = []
for block in soup.select(".future-match-single-top-wrap"):
    try:
        # Date/heure
        date_str = block.select_one(".future-match-game-title").get_text(strip=True)
        # Lieu
        venue = block.select_one(".future-match-game-title.mb-0").get_text(strip=True)
        # Placeholder équipes
        matches.append({
            "team1": "?",
            "team2": "?",
            "date": date_str,
            "venue": venue
        })
    except Exception as e:
        print(f"Erreur parsing match: {e}")

print(f"[OK] Nombre de matchs trouvés: {len(matches)}")
for m in matches[:5]:
    print(m)