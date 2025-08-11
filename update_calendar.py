import requests
from bs4 import BeautifulSoup
from icalendar import Calendar, Event
from datetime import datetime
import pytz
import subprocess

# URL de la page MLTT
URL = "https://www.mltt.com/schedule"

def fetch_matches():
    response = requests.get(URL)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    matches = []
    # À adapter selon la structure HTML exacte de mltt.com
    for match in soup.select(".match-card"):
        date_str = match.select_one(".date").text.strip()
        time_str = match.select_one(".time").text.strip()
        teams = match.select_one(".teams").text.strip()
        location = match.select_one(".location").text.strip()

        # Conversion de la date et heure
        dt_naive = datetime.strptime(f"{date_str} {time_str}", "%B %d, %Y %I:%M %p")
        tz = pytz.timezone("US/Eastern")
        dt_local = tz.localize(dt_naive)

        matches.append({
            "summary": teams,
            "location": location,
            "start": dt_local
        })
    return matches

def generate_ics(matches):
    cal = Calendar()
    cal.add("prodid", "-//MLTT Calendar//mltt.com//")
    cal.add("version", "2.0")

    for match in matches:
        event = Event()
        event.add("summary", match["summary"])
        event.add("location", match["location"])
        event.add("dtstart", match["start"])
        event.add("dtend", match["start"] + timedelta(hours=2))
        cal.add_component(event)

    return cal.to_ical().decode("utf-8")

if __name__ == "__main__":
    print("Fetching matches...")
    matches = fetch_matches()

    print("Generating ICS...")
    ics_content = generate_ics(matches)

    with open("mltt.ics", "w", encoding="utf-8") as f:
        f.write(ics_content)

    print("ICS file generated.")

    # Force un commit même si le contenu est identique
    subprocess.run(["git", "add", "mltt.ics"])
    subprocess.run(["git", "commit", "-m", "Force update MLTT calendar"], check=False)
