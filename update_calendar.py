from datetime import datetime
from ics import Calendar, Event

def create_test_ics(filename="test_event.ics"):
    cal = Calendar()
    e = Event()
    e.name = "Test Match MLTT"
    e.begin = datetime(2025, 9, 5, 16, 0)  # 5 septembre 2025 à 16h00
    e.duration = {"hours": 1}
    e.location = "Alameda County Fairgrounds, Pleasanton, CA"
    cal.events.add(e)

    with open(filename, "w") as f:
        f.writelines(cal)
    print(f"Fichier ICS de test créé : {filename}")

if __name__ == "__main__":
    create_test_ics()
