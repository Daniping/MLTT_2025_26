import requests
from bs4 import BeautifulSoup

URL = "https://mltt.com/league/schedule"  # ou la page des équipes
resp = requests.get(URL)
resp.raise_for_status()
soup = BeautifulSoup(resp.text, "html.parser")

teams = []

# On parcourt tous les items de chaque division
for item in soup.select("div.w-dyn-item a.pages-link"):
    team_name_div = item.select_one("div")
    if team_name_div:
        teams.append(team_name_div.get_text(strip=True))

print(f"{len(teams)} équipes trouvées :")
for t in teams:
    print(t)