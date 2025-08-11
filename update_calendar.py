import requests
from bs4 import BeautifulSoup
from icalendar import Calendar, Event
from datetime import datetime
import pytz
import yaml

# Lire config YAML
with open("config.yml", "r") as f:
    config = yaml.safe_load(f)

MOIS_FILTRAGE = config["filtre_mois"]
FILENAME = config["nom_fichier_ics"]
TZ = pytz.timezone(config["timezone"])

MLTT_URL = "https://www.mltt.com/schedule"

def fetch_matches():
    response = requests.get(MLTT_URL)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    matches = []
    for match in soup.select(".match-card"):  # adapte le selecteur au vrai site
        date_str = match.select_one(".match-date").text.strip()
        time_str = match.select_one(".match-time").text.strip()
        teams = match.select_one(".match-teams").text.strip()
        location = match.select_one(".match-location").text.strip()

        dt = datetime.strptime(f"{date_str} {time_str}", "%B %d, %Y %I:%M %p")
        dt = TZ.localize(dt)

        if dt.month == MOIS_FILTRAGE:
            matches.append({
                "summary": teams,
                "dtstart": dt,
                "location": location
            })
    return matches

def generate_ics(matches, filename=FILENAME):
    cal = Calendar()
    cal.add("prodid", "-//MLTT Calendar//EN")
    cal.add("version", "2.0")

    for m in matches:
        event = Event()
        event.add("summary", m["summary"])
        event.add("dtstart", m["dtstart"])
        event.add("location", m["location"])
        cal.add_component(event)

    with open(filename, "wb") as f:
        f.write(cal.to_ical())

if __name__ == "__main__":
    matchs = fetch_matches()
    generate_ics(matchs)
    print(f"Fichier {FILENAME} créé avec {len(matchs)} matchs en septembre.")

