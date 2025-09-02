# app.py

import os
import uuid
import time
import logging
from datetime import datetime, timedelta, timezone

import requests
from bs4 import BeautifulSoup
from flask import Flask, Response

# Configuration
PORT = int(os.getenv("PORT", "8080"))
SCHEDULE_URL = os.getenv("MLTT_SCHEDULE_URL",
    "https://www.mltt.com/league/schedule")
REFRESH_SECONDS = int(os.getenv("MLTT_REFRESH_SECONDS", "3600"))
EVENT_DURATION_HOURS = 4.0

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("mltt-scraper")

app = Flask(__name__)
_cache = {"ts": 0, "events": []}

# ---- Helpers ----

def parse_datetime_with_tz(text, tz_str):
    text = text.strip()
    for fmt in ["%b %d, %Y %I:%M %p", "%b %d, %Y %H:%M"]:
        try:
            dt = datetime.strptime(text, fmt)
            if tz_str.upper() == "PT":
                offset = timedelta(hours= -7)
            elif tz_str.upper() == "ET":
                offset = timedelta(hours= -4)
            else:
                offset = timedelta(0) 
            return (dt - offset).replace(tzinfo=timezone.utc)
        except:
            continue
    return None

def extract_events(html):
    soup = BeautifulSoup(html, "html.parser")
    events = []

    # On parcourt chaque semaine ("WEEK")
    for week_header in soup.select("h4"):
        if not week_header.get_text(strip=True).startswith("WEEK"):
            continue
        # Quarter events per repetition block
        next_node = week_header
        while True:
            next_node = next_node.find_next_sibling()
            if not next_node or next_node.name == "h4":
                break
            if next_node.name == "h3":
                lines = []
                tz = ""
                # Lecture jusqu'à une image "Versus"
                lv = next_node
                while lv and lv.name != "h3":
                    lines.append(lv.get_text(strip=True))
                    lv = lv.find_next_sibling()
                if len(lines) >= 3:
                    date_line = lines[0]
                    tz = lines[1]
                    location = lines[2]
                    dt = parse_datetime_with_tz(date_line, tz)
                    if dt:
                        # Récupérer équipe du bloc "Versus"
                        teams_node = next_node.find_previous(lambda tag: tag.name == "img" and "Versus" in tag.get("alt", ""))
                        summary = teams_node.get("alt", "Match") if teams_node else "Match"
                        events.append({"summary": summary,
                                       "location": location,
                                       "start_utc": dt})
    return events

def fetch_events():
    try:
        log.info(f"Scraping {SCHEDULE_URL}")
        resp = requests.get(SCHEDULE_URL, timeout=20)
        resp.raise_for_status()
        events = extract_events(resp.text)
        if not events:
            log.warning("Aucun match trouvé.")
        else:
            events.sort(key=lambda e: e["start_utc"])
            log.info(f"{len(events)} matchs extraits.")
        return events
    except Exception as e:
        log.exception("Erreur de scraping")
        return []

def get_events():
    now = time.time()
    if now - _cache["ts"] > REFRESH_SECONDS:
        _cache["events"] = fetch_events()
        _cache["ts"] = now
    return _cache["events"]

def build_ics(events):
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "CALSCALE:GREGORIAN", "PRODID:-//MLTT 2025-26//EN"]
    for ev in events:
        dtstart = ev["start_utc"]
        dtend = dtstart + timedelta(hours=EVENT_DURATION_HOURS)
        lines += [
            "BEGIN:VEVENT",
            f"UID:{uuid.uuid4()}@mltt.org",
            f"DTSTAMP:{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
            f"DTSTART:{dtstart.strftime('%Y%m%dT%H%M%SZ')}",
            f"DTEND:{dtend.strftime('%Y%m%dT%H%M%SZ')}",
            f"SUMMARY:{ev['summary']}",
            f"LOCATION:{ev['location'].replace(',', '\\,')}" if ev.get("location") else "",
            "END:VEVENT"
        ]
    lines.append("END:VCALENDAR")
    return "\n".join([l for l in lines if l]) + "\n"

# ---- Flask Routes ----

@app.route("/")
def home():
    return (
        "<h1>MLTT iCal</h1>"
        "<p>Accès au flux: <a href='/mltt.ics'>/mltt.ics</a></p>"
    )

@app.route("/mltt.ics")
def serve_ics():
    events = get_events()
    ics = build_ics(events)
    return Response(ics, mimetype="text/calendar")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)