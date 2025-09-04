# mltt_scraper.py
import re
import uuid
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
import os

URL = "https://www.mltt.com/league/schedule"
OUT_ICS = "mltt.ics"
EVENT_DURATION_HOURS = 4.0

# mapping état -> timezone IANA (ajoute si besoin)
STATE_TZ = {
    "CA": "America/Los_Angeles",
    "OR": "America/Los_Angeles",
    "WA": "America/Los_Angeles",
    "TX": "America/Chicago",
    "IL": "America/Chicago",
    "CO": "America/Denver",
    "NY": "America/New_York",
    "NC": "America/New_York",
    "GA": "America/New_York",
    "FL": "America/New_York",
    # fallback will be America/New_York
}

month_re = re.compile(r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\.?\s+\d{1,2},\s*\d{4}", re.I)

def escape_ical_text(s: str) -> str:
    if not s:
        return s
    s = s.replace("\\", "\\\\")
    s = s.replace(";", "\\;")
    s = s.replace(",", "\\,")
    s = s.replace("\n", "\\n")
    return s

def build_logo_name_map(soup):
    m = {}
    for a in soup.select("a.pages-link"):
        img = a.select_one("img")
        name_div = a.select_one("div")
        if img and name_div and name_div.get_text(strip=True):
            src = img.get("src") or ""
            m[src] = name_div.get_text(strip=True)
    return m

def parse_state_from_location(loc_text):
    # cherche "City, ST"
    m = re.search(r",\s*([A-Za-z]{2})\b", loc_text)
    if m:
        return m.group(1).upper()
    return None

def pick_datetime_from_div(div):
    # choisit le premier h3.future-match-game-title qui n'est pas city-state
    for h in div.select("h3.future-match-game-title"):
        cls = h.get("class") or []
        if "city-state" in cls:
            continue
        txt = h.get_text(" ", strip=True)
        if month_re.search(txt) and re.search(r"\d{1,2}:\d{2}", txt):
            return txt
    # fallback: first match
    first = div.select_one("h3.future-match-game-title")
    return first.get_text(" ", strip=True) if first else ""

def parse_datetime_text(dt_text, tzname):
    # formats essayés
    fmts = ["%b %d, %Y %I:%M %p", "%B %d, %Y %I:%M %p", "%Y-%m-%d %H:%M"]
    dt_text = dt_text.replace(".", "")  # enlever points de mois "Oct."
    for fmt in fmts:
        try:
            naive = datetime.strptime(dt_text, fmt)
            if tzname:
                tz = ZoneInfo(tzname)
                aware = naive.replace(tzinfo=tz)
            else:
                aware = naive.replace(tzinfo=timezone.utc)
            return aware
        except Exception:
            continue
    return None

def scrape_and_build_ics():
    r = requests.get(URL, timeout=20)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    logo_map = build_logo_name_map(soup)

    matches = []
    # on prend les blocs de match (desktop/mobile un seul type)
    for item in soup.select("div.schedule-collection-item, div.future-match-single-wrap"):
        try:
            # date/time
            dt_text = pick_datetime_from_div(item)
            # location: combine city/state and venue if present
            city_tags = item.select("h3.future-match-game-title.city-state")
            location = ", ".join([t.get_text(" ", strip=True) for t in city_tags])
            # state code from location (prefer second city-state if exists)
            state_code = parse_state_from_location(location) or parse_state_from_location(soup.get_text())
            tzname = STATE_TZ.get(state_code, "America/New_York")

            dt_site = parse_datetime_text(dt_text, tzname)
            if not dt_site:
                continue

            # teams: try to get names via logo -> name map
            team_imgs = item.select("img.future-match-single-clab-logo, div.schedule-team-logo img")
            teams = []
            for img in team_imgs:
                src = img.get("src", "")
                name = logo_map.get(src)
                if not name:
                    # try partial match
                    for k, v in logo_map.items():
                        if k and src and (k in src or src in k):
                            name = v
                            break
                if not name:
                    alt = img.get("alt", "")
                    name = alt.strip() if alt else None
                teams.append(name or "TBD")
                if len(teams) >= 2:
                    break
            if len(teams) < 2:
                # fallback: look for any nearby text with team names
                txts = item.get_text(" ", strip=True).split()
                teams = teams + ["TBD"] * (2 - len(teams))

            summary = f"{teams[0]} vs {teams[1]}"

            matches.append({
                "start": dt_site,  # aware datetime with site tz
                "summary": summary,
                "location": location or ""
            })
        except Exception:
            continue

    # build ICS
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "PRODID:-//MLTT 2025-26//EN"
    ]
    for ev in matches:
        uid = str(uuid.uuid4()) + "@mltt.org"
        start_utc = ev["start"].astimezone(timezone.utc)
        end_utc = start_utc + timedelta(hours=EVENT_DURATION_HOURS)
        dtstamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        lines.append("BEGIN:VEVENT")
        lines.append("UID:" + uid)
        lines.append("DTSTAMP:" + dtstamp)
        lines.append("DTSTART:" + start_utc.strftime("%Y%m%dT%H%M%SZ"))
        lines.append("DTEND:" + end_utc.strftime("%Y%m%dT%H%M%SZ"))
        lines.append("SUMMARY:" + escape_ical_text(ev["summary"]))
        if ev.get("location"):
            lines.append("LOCATION:" + escape_ical_text(ev["location"]))
        lines.append("END:VEVENT")

    lines.append("END:VCALENDAR")

    print("Matchs trouvés :", matches)

    with open(OUT_ICS, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"Wrote {OUT_ICS} with {len(matches)} events.")

if __name__ == "__main__":
    scrape_and_build_ics()
