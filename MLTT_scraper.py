# ==============================================================================
# MLTT_scraper_schedule.py
# - Récupère les matchs de la MLTT à partir de la page du calendrier.
# - Enregistre les matchs dans un fichier .ics.
# ==============================================================================
import datetime
import uuid
from playwright.sync_api import sync_playwright

OUTPUT_FILE = "MLTT_2025_26_V5.ics"

def create_ics_header():
    """Crée l'en-tête standard d'un fichier .ics."""
    return (
        "BEGIN:VCALENDAR\n"
        "VERSION:2.0\n"
        "PRODID:-//Gemini//MLTT Scraper//FR\n"
    )

def create_ics_footer():
    """Crée le pied de page standard d'un fichier .ics."""
    return "END:VCALENDAR\n"

def format_ics_date(date_str, time_str):
    """
    Formate une date et une heure en chaîne de caractères pour le format .ics.
    Exemple: 2025-09-05 16:00:00 -> 20250905T160000Z
    """
    # Ici, nous allons faire une estimation simple pour le format
    # car les données du site ne sont pas précises à la minute.
    # Nous supposons que le mois et le jour sont corrects.
    # L'année est une estimation basée sur la saison 2025-2026.
    try:
        # Simplification pour l'exemple
        date_obj = datetime.datetime.strptime(date_str, "%b. %d-%d, %Y")
        time_obj = datetime.datetime.strptime(time_str.split()[0], "%H:%M")
        
        # Combiner les objets datetime
        full_date = date_obj.replace(
            hour=time_obj.hour,
            minute=time_obj.minute,
            second=0
        )
        return full_date.strftime("%Y%m%dT%H%M%SZ")
    except ValueError:
        return None

def fetch_schedule():
    """
    Récupère les dates et les équipes des matchs sur le site de la MLTT.
    """
    url = "https://www.mltt.com/league/schedule"
    matches = []

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            page.goto(url, timeout=60000)
            page.wait_for_selector(".schedule-week-heading", timeout=30000)

            week_containers = page.query_selector_all(".schedule-week-container")
            
            if not week_containers:
                browser.close()
                return []

            for week_container in week_containers:
                week_title = week_container.query_selector(".schedule-week-heading").inner_text().strip()
                week_location = week_container.query_selector(".schedule-location").inner_text().strip()
                
                match_blocks = week_container.query_selector_all(".schedule-match-wrapper")

                for match_block in match_blocks:
                    try:
                        time_el = match_block.query_selector(".match-time")
                        match_time = time_el.inner_text().strip() if time_el else "00:00"
                        
                        team1_el = match_block.query_selector(".team-name.team-1")
                        team1_name = team1_el.inner_text().strip() if team1_el else "Équipe 1 inconnue"
                        
                        team2_el = match_block.query_selector(".team-name.team-2")
                        team2_name = team2_el.inner_text().strip() if team2_el else "Équipe 2 inconnue"

                        if team1_name and team2_name:
                            matches.append({
                                "date_range": week_title,
                                "time": match_time,
                                "location": week_location,
                                "team1": team1_name,
                                "team2": team2_name
                            })
                    except Exception:
                        continue
            
            browser.close()
            
    except Exception as e:
        browser.close() if 'browser' in locals() else None

    return matches

if __name__ == "__main__":
    
    schedule_data = fetch_schedule()

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(create_ics_header())
        
        for match in schedule_data:
            f.write("BEGIN:VEVENT\n")
            f.write(f"UID:{uuid.uuid4()}@mltt.com\n")
            f.write(f"DTSTAMP:{datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')}\n")
            f.write(f"SUMMARY:{match['team1']} vs {match['team2']}\n")
            
            # Formater les dates de début et de fin
            start_date_ics = format_ics_date(match['date_range'], match['time'])
            if start_date_ics:
                f.write(f"DTSTART:{start_date_ics}\n")
                # Estimation de la fin du match (2 heures)
                end_datetime = datetime.datetime.strptime(start_date_ics, '%Y%m%dT%H%M%SZ') + datetime.timedelta(hours=2)
                f.write(f"DTEND:{end_datetime.strftime('%Y%m%dT%H%M%SZ')}\n")
            
            f.write(f"LOCATION:{match['location']}\n")
            f.write("END:VEVENT\n")
            
        f.write(create_ics_footer())
