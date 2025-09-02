from flask import Flask, Response
from datetime import datetime, timedelta
import uuid

app = Flask(__name__)

def generate_ical():
    events = [
        {
            "summary": "Florida Crocs vs Bay Area Blasters",
            "location": "Pleasanton, CA",
            "start": datetime(2025, 9, 7, 14, 30),
        },
        {
            "summary": "Texas Smash vs Carolina Gold Rush",
            "location": "Houston, TX",
            "start": datetime(2025, 9, 14, 15, 0),
        }
    ]

    ical = "BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//MLTT 2025-26//EN\n"

    for ev in events:
        uid = str(uuid.uuid4()) + "@mltt.org"
        dtstart = ev["start"].strftime("%Y%m%dT%H%M%SZ")
        dtend = (ev["start"] + timedelta(hours=4)).strftime("%Y%m%dT%H%M%SZ")
        dtstamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

        ical += "BEGIN:VEVENT\n"
        ical += f"UID:{uid}\n"
        ical += f"DTSTAMP:{dtstamp}\n"
        ical += f"DTSTART:{dtstart}\n"
        ical += f"DTEND:{dtend}\n"
        ical += f"SUMMARY:{ev['summary']}\n"
        ical += (
            f"LOCATION:{ev['location'].replace(',', '\\,')}\n"
            if ev.get("location")
            else ""
        )
        ical += "END:VEVENT\n"

    ical += "END:VCALENDAR\n"
    return ical

@app.route("/mltt.ics")
def ical_feed():
    ical_data = generate_ical()
    return Response(ical_data, mimetype="text/calendar")

@app.route("/")
def home():
    return "<h1>MLTT 2025-26</h1><p>Flux iCal disponible sur <a href='/mltt.ics'>/mltt.ics</a></p>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)