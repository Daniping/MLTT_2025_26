import requests
from bs4 import BeautifulSoup
from icalendar import Calendar, Event
from datetime import datetime
import pytz

# URL du calendrier MLTT (à adapter si nécessaire)
MLTT_URL = "https://www.mltt.com/schedule"

def fetch_matches():
    response = requests.get(MLTT_URL)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    matches = []
    # Exemple de récupération (à adapter selon la structure réelle du site)
    for match in soup.select(".match-card"):
        date_str = match.select_one(".match-date").text.strip()
        time_str = match.select_one(".match-time").text.strip()
        teams = match.select_one(".match-teams").text.strip()
        location = match.select_one(".match-location").text.strip()

        # Conversion date + heure
        dt = datetime.strptime(f"{date_str} {time_str}", "%B %d, %Y %I:%M %p")
        dt = pytz.timezone("US/Eastern").localize(dt)

        matches.append({
            "summary": teams,
            "dtstart": dt,
            "location": location
        })

    return matches

def generate_ics(matches, filename="import requests
from bs4 import BeautifulSoup
from icalendar import Calendar, Event
from datetime import datetime
import pytz

# URL du calendrier MLTT (à adapter si nécessaire)
MLTT_URL = "https://www.mltt.com/schedule"

def fetch_matches():
    response = requests.get(MLTT_URL)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    matches = []
    # Exemple de récupération (à adapter selon la structure réelle du site)
    for match in soup.select(".match-card"):
        date_str = match.select_one(".match-date").text.strip()
        time_str = match.select_one(".match-time").text.strip()
        teams = match.select_one(".match-teams").text.strip()
        location = match.select_one(".match-location").text.strip()

        # Conversion date + heure
        dt = datetime.strptime(f"{date_str} {time_str}", "%B %d, %Y %I:%M %p")
        dt = pytz.timezone("US/Eastern").localize(dt)

        matches.append({
            "summary": teams,
            "dtstart": dt,
            "location": location
        })

    return matches

def generate_ics(matches, filename="MLTT_2025_26_v4"):
    cal = Calendar()
    cal.add("prodid", "-//MLTT Calendar//EN")
    cal.add("version", "2.0")

    for m in matches:
        event = Event()
        event.add("summary", m["summary"])
        event.add("dtstart", m["dtstart"])
        event.add("location", m["location"])
        cal.add_component(event)

    # ÉCRASE toujours le fichier
    with open(filename, "wb") as f:
        f.write(cal.to_ical())

if __name__ == "__main__":
    matches = fetch_matches()
    generate_ics(matches)
    print(f"Fichier mltt.ics mis à jour avec {len(matches)} matchs.")"):
    cal = Calendar()
    cal.add("prodid", "-//MLTT Calendar//EN")
    cal.add("version", "2.0")

    for m in matches:
        event = Event()
        event.add("summary", m["summary"])
        event.add("dtstart", m["dtstart"])
        event.add("location", m["location"])
        cal.add_component(event)

    # ÉCRASE toujours le fichier
    with open(filename, "wb") as f:
        f.write(cal.to_ical())

if __name__ == "__main__":
    matches = fetch_matches()
    generate_ics(matches)
    print(f"Fichier mltt.ics mis à jour avec {len(matches)} matchs.")
