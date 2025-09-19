# ==============================================================================
# MLTT_scraper_schedule.py
# - Récupère les matchs de la MLTT à partir de la page du calendrier.
# - Enregistre les matchs dans un fichier texte.
# ==============================================================================
from playwright.sync_api import sync_playwright

OUTPUT_FILE = "MLTT_matches_list.txt"

def fetch_schedule():
    """
    Récupère les dates et les équipes des matchs sur le site de la MLTT.
    """
    url = "https://www.mltt.com/league/schedule"
    matches = []

    print(f"[*] Démarrage de la récupération des données de : {url}")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # Navigue vers l'URL et attend le chargement complet de la page
            print("[*] Accès à la page du calendrier...")
            page.goto(url, timeout=60000)
            
            # Attendre que les événements du calendrier soient visibles
            print("[*] Attente du chargement du contenu...")
            page.wait_for_selector(".schedule-week-heading", timeout=30000)

            # Tous les conteneurs de week-end
            week_containers = page.query_selector_all(".schedule-week-container")
            print(f"[*] {len(week_containers)} événements de week-end trouvés.")

            if not week_containers:
                print("[!] Aucun événement de week-end n'a été trouvé. Vérifiez les sélecteurs CSS.")
                browser.close()
                return []

            for week_container in week_containers:
                # Récupère le titre et la date du week-end
                week_title = week_container.query_selector(".schedule-week-heading").inner_text().strip()
                week_location = week_container.query_selector(".schedule-location").inner_text().strip()
                
                print(f"\n--- Traitement de l'événement : {week_title} ({week_location}) ---")

                # Récupère tous les blocs de match de ce week-end
                match_blocks = week_container.query_selector_all(".schedule-match-wrapper")
                print(f"[*] {len(match_blocks)} matchs trouvés pour cette semaine.")

                for i, match_block in enumerate(match_blocks):
                    try:
                        # Récupère l'heure du match
                        time_el = match_block.query_selector(".match-time")
                        match_time = time_el.inner_text().strip() if time_el else "Heure inconnue"
                        
                        # Récupère le nom de la première équipe
                        team1_el = match_block.query_selector(".team-name.team-1")
                        team1_name = team1_el.inner_text().strip() if team1_el else "Équipe 1 inconnue"
                        
                        # Récupère le nom de la deuxième équipe
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
                            print(f"[OK] Match trouvé : {team1_name} vs {team2_name} à {match_time}")
                        else:
                            print(f"[!] Erreur de correspondance pour un match. Données : {match_block.inner_html()}")
                            
                    except Exception as e:
                        print(f"[ERREUR] Impossible d'analyser un bloc de match. Cause : {e}")
                        continue
            
            browser.close()
            
    except Exception as e:
        print(f"[ERREUR] Une erreur inattendue est survenue : {e}")
        browser.close() if 'browser' in locals() else None

    return matches

if __name__ == "__main__":
    print("[*] Début du script...")
    
    # Vider le fichier au début pour éviter d'avoir de vieilles données
    open(OUTPUT_FILE, "w", encoding="utf-8").close()

    schedule_data = fetch_schedule()

    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        for match in schedule_data:
            f.write(f"Match: {match['team1']} vs {match['team2']}\n")
            f.write(f"Date: {match['date_range']}\n")
            f.write(f"Heure: {match['time']}\n")
            f.write(f"Lieu: {match['location']}\n")
            f.write("-" * 20 + "\n")

    print(f"\n[OK] {len(schedule_data)} matchs écrits dans {OUTPUT_FILE}")
