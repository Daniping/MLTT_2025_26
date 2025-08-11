import requests
from bs4 import BeautifulSoup
from datetime import datetime
from ics import Calendar, Event

def fetch_schedule(url="https://mltt.com/2025-26-major-league-table-tennis-season"):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    schedule = []

    weekends = soup.find_all("div", class_="weekend")
    for weekend in weekends:
        weekend_name = weekend.find("h2").get_text(strip=True)

        sessions = weekend.find_all("div", class_="session")
        for session in sessions:
            session_location = session.find("span", class_="location")
            session_location = session_location.get_text(strip=True) if session_location else "Lieu non spécifié"

            matches = session.find_all("div", class_="match")
            for match in matches:
                time_str = match.find("span", class_="time").get_text(strip=True)

                date_base_str = session.find("span", class_="date").get_text(strip=True)

                try:
                    date_only = datetime.strptime(date_base_str, "%b %d, %Y")
                    time_obj = datetime.strptime(time_str, "%I:%M %p").time()
                    datetime_match = datetime.combine(date_only, time_obj)
                except Exception as e:
                    print(f"Erreur parsing date/heure match : {date_base_str} {time_str} - {e}")
                    continue

                schedule.append({
                    "weekend": weekend_name,
                    "datetime": datetime_match,
                    "location": session_location,
                })

    return schedule

def create_ics(schedule, filename="mltt_schedule_with_matches.ics"):
    cal = Calendar()

    for item in schedule:
        e = Event()
        e.name = f"{item['weekend']} - Match"
        e.begin = item["datetime"]
        e.location = item["location"]
        e.duration = {"hours": 1}  # 1h par match
        cal.events.add(e)

    with open(filename, "w") as f:
        f.writelines(cal)
    print(f"Fichier ICS avec matchs créé : {filename}")

if __name__ == "__main__":
    url = "https://mltt.com/2025-26-major-league-table-tennis-season"
    schedule = fetch_schedule(url)
    create_ics(schedule)
