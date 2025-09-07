# MLTT_scraper.py
# Écrit les matchs en clair dans MLTT_2025_26_V5.ics

def get_matches():
    # Exemple de matches récupérés — ici tu pourras remplacer par ton vrai scraping
    return [
        {"team1": "Princeton Revolution", "team2": "New York Slice"},
        {"team1": "Carolina Gold Rush", "team2": "Florida Crocs"},
        {"team1": "Texas Smash", "team2": "Chicago Wind"},
    ]

def save_matches_as_text(matches, filename="MLTT_2025_26_V5.ics"):
    # Ouvre le fichier en mode "append" pour ne rien effacer
    with open(filename, "a", encoding="utf-8") as f:
        for match in matches:
            line = f"{match['team1']} vs {match['team2']}\n"
            f.write(line)
    print(f"[OK] {len(matches)} matchs ajoutés dans {filename}")

if __name__ == "__main__":
    matches = get_matches()
    save_matches_as_text(matches)