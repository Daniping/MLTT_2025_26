from bs4 import BeautifulSoup

# soup = BeautifulSoup(HTML, "html.parser")  # ton HTML des matchs

matches = []

for match_block in soup.select(".future-match-single-wrap"):
    # Heure et lieu
    time_str = match_block.select_one(".future-match-game-title").text.strip()
    location = " | ".join([el.text.strip() for el in match_block.select(".city-state")])

    # Équipes
    teams = []
    for team_div in match_block.select(".future-match-single-clab-details"):
        name_div = team_div.select_one("div")  # ou utiliser un select plus précis si besoin
        if name_div:
            teams.append(name_div.text.strip())

    if len(teams) == 2:
        match_info = {
            "team1": teams[0],
            "team2": teams[1],
            "time": time_str,
            "location": location
        }
        matches.append(match_info)

# Exemple d’écriture ICS
lines = ["BEGIN:VCALENDAR", "VERSION:2.0"]

for m in matches:
    lines.append("BEGIN:VEVENT")
    lines.append(f"SUMMARY:{m['team1']} vs {m['team2']}")
    lines.append(f"LOCATION:{m['location']}")
    lines.append(f"DESCRIPTION:{m['team1']} vs {m['team2']} at {m['location']}")
    lines.append(f"DTSTART:{m['time']}")  # à convertir en UTC ou TZ Paris
    lines.append(f"DTEND:{m['time']}")    # idem
    lines.append("END:VEVENT")

lines.append("END:VCALENDAR")

with open("MLTT_2025_26_V5.ics", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))