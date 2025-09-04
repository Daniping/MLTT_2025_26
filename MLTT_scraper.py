import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

# Mapping logo filename → Nom d'équipe
TEAM_MAP = {
    "wind": "Chicago Wind",
    "SPINNERS": "Los Angeles Spinners",
    "SMASH": "Texas Smash",
    "BLASTERS": "Bay Area Blasters",
    "REVOLUTION": "Princeton Revolution",
    "SLICE": "New York Slice",
    "BLAZERS": "Atlanta Blazers",
    "CROCS": "Florida Crocs",
    "PADDLE": "Portland Paddlers",
    "GOLDRUSH": "Carolina Gold Rush"
}

URL = "https://www.mltt.com/schedule"
ICS_FILE = "MLTT_2025_26.ics"

def fetch_matches():
    r = requests.get(URL)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    matches = []
    for match_div in soup.select("div.schedule-for-mobile"):
        try:
            # --- Logos des équipes ---
            logos = match_div.select("img.future-match-single-clab-logo")
            teams = []
            for img in logos:
                src = img.get("src", "")
                m = re.search(r"/([^/_]+)(?:\.avif|_p-\d+\.avif)", src)
                if not m:
                    continue
                key = m.group(1).upper()
                # Cherche correspondance dans TEAM_MAP
                team_name = None
                for k, v in TEAM_MAP.items():
                    if k.upper() in src.upper():
                        team_name = v
                        break
                teams.append(team_name or key)

            team1 = teams[0] if len(teams) > 0 else "?"
            team2 = teams[1] if len(teams) > 1 else "?"

            # --- Date & heure ---
            date_tag = match_div.select_one("div.match-time-flex h3")
            date_str = date_tag.get_text(strip=True) if date_tag else None
            try:
                dt = datetime.strptime(date_str, "%b %d, %Y %I:%M %p")
            except Exception:
                dt = None

            # --- Lieu ---
            venue_tag = match_div.select("h3.future-match-game-title")
            venue = venue_tag[-1].get_text(strip=True) if venue_tag else "Unknown Venue"

            # --- Ticket link ---
            ticket_tag = match_div.select_one("a.primary-btn-link-wrap")
            ticket_url = ticket_tag["href"] if ticket_tag else None

            matches.append({
                "team1": team1,
                "team2": team2,
                "date": dt,
                "venue": venue,
                "ticket": ticket_url
            })

        except Exception as e:
            print("[WARN] Erreur parsing match:", e)

    return matches

def save_ics(matches):
    with open(ICS_FILE, "w", encoding="utf-8") as f:
        f.write("BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//MLTT//EN\n")
        for i, m in enumerate(matches):
            if not m["date"]:
                continue
            dtstamp = m["date"].strftime("%Y%m%dT%H%M%S")
            dtend = (m["date"]).strftime("%Y%m%dT%H%M%S")
            f.write("BEGIN:VEVENT\n")
            f.write(f"UID:mltt-{i}@mltt.com\n")
            f.write(f"DTSTAMP:{dtstamp}\n")
            f.write(f"DTSTART:{dtstamp}\n")
            f.write(f"DTEND:{dtend}\n")
            f.write(f"SUMMARY:{m['team1']} vs {m['team2']}\n")
            f.write(f"LOCATION:{m['venue']}\n")
            if m["ticket"]:
                f.write(f"URL:{m['ticket']}\n")
            f.write("END:VEVENT\n")
        f.write("END:VCALENDAR\n")

if __name__ == "__main__":
    matches = fetch_matches()
    print(f"[OK] Nombre de matchs trouvés: {len(matches)}")
    for m in matches[:5]:
        print(m)
    save_ics(matches)
    print(f"[OK] {ICS_FILE} généré avec {len(matches)} événements.")