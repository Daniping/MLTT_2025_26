# app.py — version finale prête à coller
import os
import re
import uuid
import time
import logging
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import requests
from bs4 import BeautifulSoup
from flask import Flask, Response

# ---- config ----
PORT = int(os.getenv("PORT", "8080"))
SCHEDULE_URL = os.getenv("MLTT_SCHEDULE_URL", "https://www.mltt.com/league/schedule")
REFRESH_SECONDS = int(os.getenv("MLTT_REFRESH_SECONDS", "1800"))  # cache 30 min
EVENT_DURATION_HOURS = float(os.getenv("MLTT_EVENT_HOURS", "4.0"))

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; MLTT-ICS/1.0)"}

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("mltt-scraper")

app = Flask(__name__)
_cache = {"ts": 0, "events": []}

# ---- timezone map (IANA names) ----
TZ_MAP = {
    "PT": "America/Los_Angeles",
    "PST": "America/Los_Angeles",
    "PDT": "America/Los_Angeles",
    "ET": "America/New_York",
    "EST": "America/New_York",
    "EDT": "America/New_York",
    "CT": "America/Chicago",
    "MT": "America/Denver",
}

# regex to find date/time strings like "Sep 5, 2025 4:00 PM"
date_re = re.compile(r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\.?\s+\d{1,2},\s*\d{4}\s+\d{1,2}:\d{2}\s*(?:AM|PM)?", re.I)

# ---- helpers ----
def parse_datetime_with_zone(dt_text, tz_label=None):
    dt_text = dt_text.strip()
    fmts = ["%b %d, %Y %I:%M %p", "%B %d, %Y %I:%M %p", "%Y-%m-%d %H:%M", "%m/%d/%Y %I:%M %p"]
    for fmt in fmts:
        try:
            naive = datetime.strptime(dt_text, fmt)
            if tz_label and tz_label.upper() in TZ_MAP:
                tz = ZoneInfo(TZ_MAP[tz_label.upper()])
            else:
                tz = timezone.utc
            aware = naive.replace(tzinfo=tz)
            return aware.astimezone(timezone.utc)
        except Exception:
            continue
    return None

def escape_ical_text(s: str) -> str:
    if not s:
        return s
    s = s.replace("\\", "\\\\")
    s = s.replace(";", "\\;")
    s = s.replace(",", "\\,")
    s = s.replace("\n", "\\n")
    return s

# ---- scraping ----
def extract_events_from_html(html):
    soup = BeautifulSoup(html, "html.parser")
    events = []
    seen = set()

    # find all images with alt containing "versus" (robust for this site)
    versus_imgs = [img for img in soup.find_all("img") if img.get("alt") and "versus" in img.get("alt", "").lower()]

    for vs in versus_imgs:
        try:
            # team names from nearby images with alt (skip "versus")
            team1 = None; team2 = None
            prev_img = vs.find_previous("img")
            while prev_img and (not prev_img.get("alt") or "versus" in prev_img.get("alt", "").lower()):
                prev_img = prev_img.find_previous("img")
            if prev_img and prev_img.get("alt"):
                team1 = prev_img.get("alt").strip()

            next_img = vs.find_next("img")
            while next_img and (not next_img.get("alt") or "versus" in next_img.get("alt", "").lower()):
                next_img = next_img.find_next("img")
            if next_img and next_img.get("alt"):
                team2 = next_img.get("alt").strip()

            # find datetime text near the versus image
            dt_node = vs.find_previous(lambda tag: tag.name in ("h1","h2","h3","h4","p","div","span") and tag.get_text(strip=True) and date_re.search(tag.get_text(strip=True)))
            if dt_node is None:
                dt_node = vs.find_next(lambda tag: tag.name in ("h1","h2","h3","h4","p","div","span") and tag.get_text(strip=True) and date_re.search(tag.get_text(strip=True)))

            dt_text = dt_node.get_text(" ", strip=True) if dt_node else ""
            m = date_re.search(dt_text) if dt_text else None
            dt_parsed = None
            if m:
                dt_parsed = parse_datetime_with_zone(m.group(0), None)

            # search for timezone label (PT/ET) near dt_node
            tz_label = None
            if dt_node:
                for sib in dt_node.find_all_next(limit=8):
                    text = (sib.get_text(strip=True) or "").strip()
                    if text.upper() in TZ_MAP:
                        tz_label = text.upper(); break
                if not tz_label:
                    for sib in dt_node.find_all_previous(limit=8):
                        text = (sib.get_text(strip=True) or "").strip()
                        if text.upper() in TZ_MAP:
                            tz_label = text.upper(); break
            if m and tz_label:
                dt_parsed = parse_datetime_with_zone(m.group(0), tz_label)

            # venue search
            location = ""
            if dt_node:
                loc_parts = []
                for node in dt_node.find_all_next(limit=12):
                    txt = node.get_text(" ", strip=True)
                    if not txt:
                        continue
                    if any(k in txt for k in ("Convention", "Fairgrounds", "Center", "Arena", "Field", "VBC", "Memorial")):
                        loc_parts.append(txt)
                    if re.search(r"[A-Za-z .]+,\s*[A-Z]{2}\b", txt):
                        loc_parts.append(txt); break
                    if re.match(r"^[A-Za-z .]+,\s*[A-Z]{2}$", txt):
                        loc_parts.append(txt); break
                if loc_parts:
                    location = ", ".join(dict.fromkeys(loc_parts))

            if not dt_parsed:
                continue

            if team1 and team2:
                summary = f"{team1} vs {team2}"
            else:
                summary = (team1 or "") + " vs " + (team2 or "")
                summary = summary.strip()

            key = (dt_parsed.isoformat(), summary)
            if key in seen:
                continue
            seen.add(key)

            events.append({
                "summary": escape_ical_text(summary),
                "location": escape_ical_text(location),
                "start_utc": dt_parsed,
            })
        except Exception as e:
            log.debug("skip one vs block: %s", e)
            continue

    events.sort(key=lambda e: e["start_utc"])
    return events

def fetch_events():
    try:
        log.info("Requesting schedule page %s", SCHEDULE_URL)
        r = requests.get(SCHEDULE_URL, headers=HEADERS, timeout=20)
        r.raise_for_status()
        events = extract_events_from_html(r.text)
        if not events:
            log.warning("No events found on page.")
        else:
            log.info("Found %d events.", len(events))
        return events
    except Exception:
        log.exception("Scrape failed")
        return []

def get_events_cached():
    now = time.time()
    if now - _cache["ts"] > REFRESH_SECONDS or not _cache["events"]:
        _cache["events"] = fetch_events()
        _cache["ts"] = now
    return _cache["events"]

# ---- ICS builder ----
def build_ics(events):
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "PRODID:-//MLTT 2025-26//EN"
    ]
    for ev in events:
        uid = f"{uuid.uuid4()}@mltt.org"
        dtstart = ev["start_utc"].astimezone(timezone.utc)
        dtend = dtstart + timedelta(hours=EVENT_DURATION_HOURS)
        dtstamp = datetime.now(timezone.utc)
        lines.append("BEGIN:VEVENT")
        lines.append(f"UID:{uid}")
        lines.append(f"DTSTAMP:{dtstamp.strftime('%Y%m%dT%H%M%SZ')}")
        lines.append(f"DTSTART:{dtstart.strftime('%Y%m%dT%H%M%SZ')}")
        lines.append(f"DTEND:{dtend.strftime('%Y%m%dT%H%M%SZ')}")
        lines.append(f"SUMMARY:{ev['summary']}")
        if ev.get("location"):
            lines.append(f"LOCATION:{ev['location']}")
        lines.append("END:VEVENT")
    lines.append("END:VCALENDAR")
    return "\n".join(lines) + "\n"

# ---- flask routes ----
@app.route("/")
def home():
    src = SCHEDULE_URL or "(none)"
    return f"<h1>MLTT iCal</h1><p>Flux: <a href='/mltt.ics'>/mltt.ics</a></p><p>Source: {src}</p>"

@app.route("/mltt.ics")
def mltt_ics():
    events = get_events_cached()
    if not events:
        return Response("BEGIN:VCALENDAR\nVERSION:2.0\nEND:VCALENDAR\n", mimetype="text/calendar")
    ics = build_ics(events)
    return Response(ics, mimetype="text/calendar")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)