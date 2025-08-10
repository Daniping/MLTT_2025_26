import requests
from bs4 import BeautifulSoup
from icalendar import Calendar, Event
from datetime import datetime
import pytz

def fetch_mltt_matches():
    url = "https://mltt.com/schedule"  # Exemple, à ajuster selon l'URL exacte
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    # Exemple : chercher les matchs dans la page (à adapter selon la structure réelle)
    matches = []
    for match_div in soup.select(".match"):  # sélecteur fictif
        date_str = match_div.select_one(".date").text.strip()
        time_str = match_div.select_one(".time").text.strip()
        team1 = match_div.select_one(".team1").text.strip()
        team2 = match_div.select_one(".team2").text.strip()
        location = match_div.select_one(".location").text.strip()

        # Convertion date + heure en datetime
        dtstart = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        dtstart = pytz.UTC.localize(dtstart)

        matches.append({
            "summary": f"{team1} vs {team2}",
            "dtstart": dtstart,
            "dtend": dtstart.replace(hour=dtstart.hour+2),  # match 2h par défaut
            "location": location,
            "description": f"Match between {team1} and {team2}"
        })
    return matches

def create_ics(matches):
    cal = Calendar()
    cal.add("prodid", "-//MLTT 2025-26//FR")
    cal.add("version", "2.0")
    cal.add("X-WR-CALNAME", "MLTT 2025-26")

    for i, match in enumerate(matches):
        event = Event()
        event.add("uid", f"mltt-{i}@mltt.com")
        event.add("summary", match["summary"])
        event.add("dtstart", match["dtstart"])
        event.add("dtend", match["dtend"])
        event.add("location", match["location"])
        event.add("description", match["description"])
        cal.add_component(event)

    with open("mltt.ics", "wb") as f:
        f.write(cal.to_ical())

def main():
    matches = fetch_mltt_matches()
    create_ics(matches)

if __name__ == "__main__":
    main()
