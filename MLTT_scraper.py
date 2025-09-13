import requests
from bs4 import BeautifulSoup

url = "https://mltt.com/teams"

response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

teams = []

# Les noms d'équipes sont dans des balises <h2> sur la page
for h2 in soup.find_all("h2"):
    name = h2.get_text(strip=True)
    if name:  # éviter les vides
        teams.append(name)

print("Équipes MLTT trouvées :")
for team in teams:
    print("-", team)