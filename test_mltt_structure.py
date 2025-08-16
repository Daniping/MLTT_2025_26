import os
import re
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import requests
from bs4 import BeautifulSoup
from icalendar import Calendar, Event

MLTT_URL = "https://www.mltt.com/league/schedule"

# --------- Réglages heure ----------
TZ_PARIS = ZoneInfo("Europe/Paris")

# Mapping simple État US -> fuseau
STATE_TZ = {
    # Eastern
    "CT":"America/New_York","DC":"America/New_York","DE":"America/New_York","FL":"America/New_York",
    "GA":"America/New_York","MA":"America/New_York","MD":"America/New_York","ME":"America/New_York",
    "NH":"America/New_York","NJ":"America/New_York","NY":"America/New_York","NC":"America/New_York",
    "OH":"America/New_York","PA":"America/New_York","RI":"America/New_York","SC":"America/New_York",
    "VA":"America/New_York","VT":"America/New_York","MI":"America/New_York","IN":"America/Indiana/Indianapolis",
    # Central
    "AL":"America/Chicago","AR":"America/Chicago","IA":"America/Chicago","IL":"America/Chicago",
    "KS":"America/Chicago","KY":"America/Chicago","LA":"America/Chicago","MN":"America/Chicago",
    "MO":"America/Chicago","MS":"America/Chicago","ND":"America/Chicago","NE":"America/Chicago",
    "OK":"America/Chicago","SD":"America/Chicago","TN":"America/Chicago","TX":"America/Chicago",
    "WI":"America/Chicago",
    # Mountain
    "AZ":"America/Phoenix","CO":"America/Denver","MT":"America/Denver","NM":"America/Denver",
    "UT":"America/Denver","WY":"America/Denver","ID":"America/Boise",
    # Pacific
    "CA":"America/Los_Angeles","NV":"America/Los_Angeles","OR":"America/Los_Angeles","WA":"America/Los_Angeles",
    # Hawaii / Alaska
    "HI":"Pacific/Honolulu","AK":"America/Anchorage"
}

# Regex date & heure (ex: "Mar 22, 2026 2:30 PM")
DATE_RE = re.compile(r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},\s+\d{4}\b")
TIME_RE = re.compile(r"\b\d{1,2}:\d{2}\s*(AM|PM)\b", re.IGNORECASE)
STATE_RE = re.compile(r",\s*(AL|AK|AZ|AR|CA|CO|CT|DC|DE|FL|GA|HI|IA|ID|IL|IN|KS|KY|LA|MA|MD|ME|MI|MN|MO|MS|MT|NC|ND|NE|NH|NJ|NM|NV|NY|OH|OK|OR|PA|RI|SC|SD|TN|TX|UT|VA|VT|WA|WI|WV)\b")

def detect_timezone(location_text: str):
    m = STATE_RE.search(location_text or "")
    if not m:
        return ZoneInfo("America/New_York")  # par défaut (beaucoup d’événements côté Est)
    state = m.group(1)
    return ZoneInfo(STATE_TZ.get(state, "America/New_York"))

def parse_block_to_event(block_text: str):
    """Renvoie (start_dt_paris, location) ou None si non exploitable."""
    date_m = DATE_RE.search(block_text)
    time_m = TIME_RE.search(block_text)
    if not date_m or not time_m:
        return None

    dt_str = f"{date_m.group(0)} {time_m.group(0).upper()}"
    try:
        naive = datetime.strptime(dt_str, "%b %d, %Y %I:%M %p")
    except ValueError:
        return None

    # Heuristique lieu = dernière ligne contenant une virgule + État (ex: "Lawrenceville, NJ")
    location_line = ""
    for line in block_text.splitlines():
        if STATE_RE.search(line):
            location_line = line.strip()

    tz_src = detect_timezone(location_line)
    start_local = naive.replace(tzinfo=tz_src)
    start_paris = start_local.astimezone(TZ_PARIS)
    location = location_line or "Lieu inconnu"
    return start_paris, location

def main():
    print(f"🔍 Lecture de la page : {MLTT_URL}")
    r = requests.get(MLTT_URL, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    print(f"✅ Page téléchargée avec succès à : {datetime.now(TZ_PARIS).strftime('%Y-%m-%d %H:%M:%S')}")

    events = []

    # On parcourt chaque <h3> et on construit un "bloc" avec ce <h3> + quelques siblings suivants
    for h3 in soup.find_all("h3"):
        # Construire un bloc de texte compact (h3 + 4 siblings)
        parts = [h3.get_text(" ", strip=True)]
        sib = h3.find_next_sibling()
        for _ in range(4):
            if not sib:
                break
            parts.append(sib.get_text(" ", strip=True))
            sib = sib.find_next_sibling()
        block = "\n".join([p for p in parts if p])

        # Filtrage bruit évident
        if "Your cart" in block or "Cart" in block:
            continue

        parsed = parse_block_to_event(block)
        if parsed:
            start_paris, location = parsed
            events.append({"start": start_paris, "end": start_paris + timedelta(hours=2), "location": location})
            print(f"🟢 Match: {start_paris.strftime('%Y-%m-%d %H:%M')} (Paris) — {location}")

    # Génération ICS (ne plante pas si vide)
    cal = Calendar()
    cal.add("prodid", "-//MLTT Calendar V5//mltt.com//")
    cal.add("version", "2.0")
    cal.add("calscale", "GREGORIAN")
    cal.add("X-WR-CALNAME", "MLTT – Matches (Heure de Paris)")

    for i, e in enumerate(events):
        evt = Event()
        evt.add("uid", f"mltt-{i}@mltt.com")
        evt.add("dtstamp", datetime.now(TZ_PARIS))
        evt.add("dtstart", e["start"])
        evt.add("dtend", e["end"])
        evt.add("summary", "MLTT Match")
        evt.add("location", e["location"])
        cal.add_component(evt)

    os.makedirs("MLTT_2025_26_V5", exist_ok=True)
    ics_path = "MLTT_2025_26_V5/MLTT_2025_26_V5.ics"
    with open(ics_path, "wb") as f:
        f.write(cal.to_ical())

    print(f"✅ Fichier ICS généré : {ics_path}")
    print(f"ℹ️ Événements trouvés : {len(events)}")

if __name__ == "__main__":
    main()
