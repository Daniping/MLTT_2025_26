from flask import Flask, Response
from ics import Calendar, Event
from datetime import datetime, timedelta

app = Flask(__name__)

matches = [
    ("2025-09-05 16:00", "Florida Crocs", "Portland Paddlers", "Pleasanton, CA"),
    ("2025-09-05 19:30", "Texas Smash", "Bay Area Blasters", "Pleasanton, CA"),
    ("2025-09-06 16:00", "Florida Crocs", "Texas Smash", "Pleasanton, CA"),
    ("2025-09-06 19:30", "Portland Paddlers", "Bay Area Blasters", "Pleasanton, CA"),
    ("2025-09-07 11:00", "Portland Paddlers", "Texas Smash", "Pleasanton, CA"),
    ("2025-09-07 14:30", "Florida Crocs", "Bay Area Blasters", "Pleasanton, CA"),
    ("2025-09-19 19:30", "Atlanta Blazers", "Carolina Gold Rush", "Charlotte, NC"),
    ("2025-09-20 19:30", "Florida Crocs", "Carolina Gold Rush", "Charlotte, NC"),
    ("2025-09-21 14:30", "New York Slice", "Carolina Gold Rush", "Charlotte, NC"),
    ("2025-10-03 19:30", "Los Angeles Spinners", "Portland Paddlers", "Portland, OR"),
    ("2025-10-04 16:00", "Carolina Gold Rush", "Los Angeles Spinners", "Portland, OR"),
    ("2025-10-04 19:30", "Chicago Wind", "Portland Paddlers", "Portland, OR"),
    ("2025-10-05 14:30", "Carolina Gold Rush", "Portland Paddlers", "Portland, OR"),
    # … ajouter toutes les autres semaines de la même manière …
]

@app.route('/mltt.ics')
def mltt_ical():
    c = Calendar()
    for dt_str, team1, team2, location in matches:
        e = Event()
        e.name = f"{team1} vs {team2}"
        e.begin = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
        e.duration = timedelta(hours=1, minutes=30)
        e.location = location
        c.events.add(e)
    return Response(str(c), mimetype='text/calendar')

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
