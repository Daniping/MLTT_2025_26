import requests
from bs4 import BeautifulSoup

MLTT_URL = "https://www.mltt.com/league/schedule"

print(f"🔍 Lecture de la page : {MLTT_URL}")
r = requests.get(MLTT_URL)
r.raise_for_status()
soup = BeautifulSoup(r.text, "html.parser")

from datetime import datetime
from zoneinfo import ZoneInfo

# Exemple : texte récupéré depuis la page = "Aug 20, 2025 7:00 PM"
match_time_str = "Aug 20, 2025 7:00 PM"

# On précise que l'heure récupérée est en fuseau horaire Californie
us_time = datetime.strptime(match_time_str, "%b %d, %Y %I:%M %p").replace(tzinfo=ZoneInfo("America/Los_Angeles"))

# Conversion en heure de Paris
paris_time = us_time.astimezone(ZoneInfo("Europe/Paris"))

print("Heure Californie :", us_time.strftime("%Y-%m-%d %H:%M"))
print("Heure Paris :", paris_time.strftime("%Y-%m-%d %H:%M"))

print(f"✅ Page téléchargée avec succès à : {datetime.now(ZoneInfo('Europe/Paris')).strftime('%Y-%m-%d %H:%M:%S')}")

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
