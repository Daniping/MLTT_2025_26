from flask import Flask, Response
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

MLTT_URL = "https://example.com/mltt-schedule"  # Remplace par l’URL de ton planning réel

def generate_ics():
    events = []

    # Récupération de la page
    resp = requests.get(MLTT_URL)
    soup = BeautifulSoup(resp.text, "html.parser")

    # Exemple : on parcourt tous les matchs dans la page
    for match_div in soup.select(".match"):  # Adapte le sélecteur à ton HTML
        teams = match_div.select_one(".teams").text.strip()
        dt_str = match_div.select_one(".datetime").text.strip()  # Ex: "2025-09-07 14:30"
        dt_start = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
        dt_end = dt_start + timedelta(hours=4)  # durée estimée

        location = match_div.select_one(".location").text.strip()

        event = f"""BEGIN:VEVENT
SUMMARY:{teams}
DTSTART:{dt_start.strftime('%Y%m%dT%H%M%SZ')}
DTEND:{dt_end.strftime('%Y%m%dT%H%M%SZ')}
LOCATION:{location}
UID:{teams.replace(' ', '')}-{dt_start.strftime('%Y%m%dT%H%M%S')}@mltt.org
END:VEVENT"""
        events.append(event)

    ics_content = "BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//MLTT 2025-26//EN\n"
    ics_content += "\n".join(events)
    ics_content += "\nEND:VCALENDAR"
    return ics_content

@app.route("/")
def index():
    return "<h1>Bienvenue sur MLTT 2025-26 !</h1><p>Pour télécharger le calendrier : <a href='/mltt.ics'>mltt.ics</a></p>"

@app.route("/mltt.ics")
def mltt_ics():
    ics_data = generate_ics()
    return Response(ics_data, mimetype="text/calendar", headers={
        "Content-Disposition": "attachment; filename=mltt.ics"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)