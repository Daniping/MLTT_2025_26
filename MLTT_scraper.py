import requests
from bs4 import BeautifulSoup

URL = "https://mltt.com/league/schedule"  # URL du calendrier MLTT

# Récupérer la page
resp = requests.get(URL)
resp.raise_for_status()
soup = BeautifulSoup(resp.text, "html.parser")

# Récupérer toutes les équipes dans l'ordre du dropdown
team_divs = soup.select(".pages-drop-down-single-wrap .w-dyn-item div")
teams = [d.get_text(strip=True) for d in team_divs]

print("Toutes les équipes trouvées :")
for t in teams:
    print("-", t)

# Récupérer les blocs de matchs
match_blocks = soup.select(".future-match-single-wrap")

matches = []
for mb in match_blocks:
    try:
        # Les indices ou informations dans le HTML qui pointent vers les équipes
        idx1 = int(mb.get("data-team1-index", -1))
        idx2 = int(mb.get("data-team2-index", -1))
        
        team1 = teams[idx1] if 0 <= idx1 < len(teams) else "?"
        team2 = teams[idx2] if 0 <= idx2 < len(teams) else "?"
        
        matches.append({"team1": team1, "team2": team2})
    except Exception as e:
        print("Erreur match:", e)

print("\nMatchs récupérés :")
for m in matches:
    print(m["team1"], "vs", m["team2"])