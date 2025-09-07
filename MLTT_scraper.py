# ===========================================
# MLTT_scraper.py - Test 1 match avec D,H,L
# Objectif : Scraper un match et l'écrire
# dans MLTT_2025_26_V5.ics avec Date, Heure, Lieu
# ===========================================

from datetime import datetime

# ==============================
# Définition du fichier de sortie
# ==============================
OUTPUT_FILE = "MLTT_2025_26_V5.ics"

# ==============================
# Simuler un match récupéré
# ==============================
match = {
    "team1": "Princeton Revolution",
    "team2": "New York Slice",
    "date": "2025-09-05T16:00:00",  # ISO format
    "venue": "ALAMEDA COUNTY FAIRGROUNDS"
}

# ==============================
# Extraire la date et l'heure
# ==============================
dt_obj = datetime.fromisoformat(match['date'])
date_str = dt_obj.strftime("%Y-%m-%d")
time_str = dt_obj.strftime("%H:%M")

# ==============================
# Construire la ligne à écrire
# ==============================
line = f"{match['team1']} vs {match['team2']} - Date: {date_str}, Heure: {time_str}, Lieu: {match['venue']}\n"

# ==============================
# Écriture dans le fichier
# ==============================
with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
    f.write(line)

# ==============================
# Confirmation dans le log
# ==============================
print(f"[OK] Match écrit dans {OUTPUT_FILE} avec Date, Heure et Lieu")