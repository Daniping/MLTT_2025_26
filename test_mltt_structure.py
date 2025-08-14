import requests
from bs4 import BeautifulSoup

MLTT_URL = "https://www.mltt.com/league/schedule"

print(f"🔍 Lecture de la page : {MLTT_URL}")
r = requests.get(MLTT_URL)
r.raise_for_status()
soup = BeautifulSoup(r.text, "html.parser")
print("✅ Page téléchargée avec succès.")

# Recherche des matchs : chaque <h3> suivi d'un div contenant les équipes et le lieu
matches = soup.select("h3 + div")

if not matches:
    print("⚠️ Aucun match trouvé avec le sélecteur h3 + div")
else:
    print(f"✅ {len(matches)} matchs trouvés.\n")

# Affichage des équipes, dates et lieux
for i, h3 in enumerate(matches, 1):
    title = h3.get_text(strip=True)  # souvent la date ou titre du match
    match_div = h3.find_next_sibling()
    if not match_div:
        continue

    # Extraction des équipes et du lieu
    teams_text = match_div.get_text(" ", strip=True)
    if " vs " in teams_text:
        teams_part, *location_part = teams_text.split(" à ")
        team1, team2 = teams_part.split(" vs ")
        location = location_part[0] if location_part else "Lieu inconnu"
    else:
        team1 = team2 = location = "Non trouvé"

    print(f"Match {i} : {team1} vs {team2}")
    print(f"Date/Heure (titre) : {title}")
    print(f"Lieu : {location}")
    print("\n")
