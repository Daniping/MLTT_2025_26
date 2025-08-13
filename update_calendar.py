import requests
from bs4 import BeautifulSoup
from icalendar import Calendar, Event
from datetime import datetime, timedelta
import pytz

MLTT_URL = "https://www.mltt.com/league/schedule"

def fetch_september_matches():
    r = requests.get(MLTT_URL)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    events = []
    for item in soup.select(".upcoming-matches li"):
        text = item.get_text(separator=" ", strip=True)
        # Exemple : "Sep 5, 2025 4:00 PM Alameda County Fairgrounds Pleasanton, CA"
        parts = text.split(" ")
        if parts[0] != "Sep":
            continue  # On ne garde que septembre

        try:
            dt_str = " ".join(parts[:5])  # "Sep 5, 2025 4:00 PM"
            dt = datetime.strptime(dt_str, "%b %d, %Y %I:%M %p")
            # Le lieu est le reste du texte
            location = " ".join(parts[5:])
            dt_utc = pytz.timezone("US/Pacific").localize(dt).astimezone(pytz.UTC)
            events.append({
                "dtstart": dt_utc,
                "dtend": dt_utc + timedelta(hours=2),
                "summary": f"MLTT Event - {dt.strftime('%b %d %H:%M')}",
                "location": location
            })
        except Exception:
            continue

    return events

def generate_ics(events, filename="MLTT_2025_26_V4.ics"):
    cal = Calendar()
    cal.add("prodid", "-//MLTT Calendar//mltt.com//")
    cal.add("version", "2.0")
    cal.add("calscale", "GREGORIAN")
    cal.add("X-WR-CALNAME", "MLTT – Septembre 2025")

    for i, e in enumerate(events):
        evt = Event()
        evt.add("uid", f"mltt-sep2025-{i}@mltt.com")
        evt.add("dtstamp", datetime.now(pytz.UTC))
        evt.add("dtstart", e["dtstart"])
        evt.add("dtend", e["dtend"])
        evt.add("summary", e["summary"])
        evt.add("location", e["location"])
        cal.add_component(evt)

    with open(filename, "wb") as f:
        f.write(cal.to_ical())

if __name__ == "__main__":
    evs = fetch_september_matches()
    if evs:
        generate_ics(evs)
        print(f"✅ {len(evs)} événements de septembre exportés dans le fichier.")
    else:
        # On crée le fichier quand même pour forcer le push
        generate_ics([])
        print("ℹ️ Aucun événement trouvé pour septembre, fichier créé vide.")
