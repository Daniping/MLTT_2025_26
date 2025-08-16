import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from icalendar import Calendar, Event
import os

MLTT_URL = "https://www.mltt.com/league/schedule"

print(f"🔍 Lecture de la page : {MLTT_URL}")
r = requests.get(MLTT_URL)
r.raise_for_status()
soup = BeautifulSoup(r.text, "html.parser")

# Heure de l'extraction
now_paris = datetime.now(ZoneInfo("Europe/Paris"))
print(f"✅ Page téléchargée avec succès à : {now_paris.strftime('%Y-%m-%d %H:%M:%S')}")

# Recherche des vrais matchs : <h3> suivi d'un <div class="match">
matches = []
for h3 in soup.find_all("h3"):
    sibling = h3.find_next_sibling()
    if sibling and sibling.name == "div" and "match" in sibling.get("class", []):
        matches.append((h3, sibling))

if not matches:
    print("⚠️ Aucun match trouvé avec le sélecteur h3 + div.match")
else:
    print(f"✅ {len(matches)} matchs trouvés")

# Création du calendrier
cal = Calendar()
cal.add("prodid", "-//MLTT Calendar V5//mxm.dk//")
cal.add("version", "2.0")

tz_paris = ZoneInfo("Europe/Paris")

for h3, div in matches:
    # Extraction des infos
    date_text = div.find("span", class_="match-date")  # ou adapter selon la page
    time_text = div.find("span", class_="match-time")  # idem
    location = div.find("span", class_="match-location")  # idem

    if date_text and time_text:
        datetime_str = f"{date_text.get_text(strip=True)} {time_text.get_text(strip=True)}"
        # On suppose que l'heure sur le site est en Californie
        start_dt = datetime.strptime(datetime_str, "%b %d, %Y %I:%M %p").replace(tzinfo=ZoneInfo("America/Los_Angeles"))
        start_dt = start_dt.astimezone(tz_paris)
    else:
        continue

    lieu = location.get_text(strip=True) if location else "Lieu inconnu"

    event = Event()
    event.add("summary", "MLTT Match")
    event.add("dtstart", start_dt)
    event.add("dtend", start_dt + timedelta(hours=2))
    event.add("location", lieu)
    cal.add_component(event)

# Création du dossier et écriture du fichier ICS
os.makedirs("MLTT_2025_26_V5", exist_ok=True)
ics_filename = "MLTT_2025_26_V5/MLTT_2025_26_V5.ics"
with open(ics_filename, "wb") as f:
    f.write(cal.to_ical())

print(f"✅ Fichier ICS généré : {ics_filename}")
