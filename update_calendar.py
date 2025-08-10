import requests
from bs4 import BeautifulSoup
from icalendar import Calendar, Event
from datetime import datetime, timedelta
import pytz

def fetch_schedule():
    url = "https://mltt.com/schedule"  # Remplace par la vraie URL du planning si différente
    r = requests.get(url)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, 'html.parser')
    
    # Exemple simplifié : on récupère tous les éléments de match (à adapter)
    matches = []
    for match_div in soup.select('.match'):  # Ajuste le sélecteur CSS selon la page
        date_str = match_div.select_one('.date').text.strip()   # Ex: '2025-09-05 16:00'
        team1 = match_div.select_one('.team1').text.strip()
        team2 = match_div.select_one('.team2').text.strip()
        location = match_div.select_one('.location').text.strip()
        desc = match_div.select_one('.description').text.strip()

        dtstart = datetime.strptime(date_str, '%Y-%m-%d %H:%M')
        dtstart = pytz.UTC.localize(dtstart)  # On suppose UTC, à ajuster si besoin
        dtend = dtstart + timedelta(hours=2)  # Durée 2h par défaut

        matches.append({
            'summary': f"{team1} vs {team2}",
            'dtstart': dtstart,
            'dtend': dtend,
            'location': location,
            'description': desc,
            'uid': f"mltt-{dtstart.strftime('%Y%m%d%H%M')}-{team1[:3]}{team2[:3]}@mltt.com"
        })
    return matches

def create_ics(matches):
    cal = Calendar()
    cal.add('prodid', '-//MLTT 2025-26//FR')
    cal.add('version', '2.0')
    cal.add('calscale', 'GREGORIAN')
    cal.add('X-WR-CALNAME', 'MLTT 2025-26')

    for m in matches:
        event = Event()
        event.add('uid', m['uid'])
        event.add('dtstamp', datetime.now(pytz.UTC))
        event.add('dtstart', m['dtstart'])
        event.add('dtend', m['dtend'])
        event.add('summary', m['summary'])
        event.add('location', m['location'])
        event.add('description', m['description'])
        cal.add_component(event)
    return cal.to_ical()

def main():
    matches = fetch_schedule()
    ics_content = create_ics(matches)
    with open('mltt.ics', 'wb') as f:
        f.write(ics_content)
    print("mltt.ics mis à jour avec", len(matches), "matchs.")

if __name__ == "__main__":
    main()
