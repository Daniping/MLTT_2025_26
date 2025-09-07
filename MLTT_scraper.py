# ===========================================
# MLTT_scraper.py - Test 1 match
# Objectif : Scraper un match et l'écrire
# dans MLTT_2025_26_V5.ics comme un simple texte
# ===========================================

from datetime import datetime

# ==============================
# Définition du fichier de sortie
# ==============================
OUTPUT_FILE = "MLTT_2025_26_V5.ics"

# ==============================
# Simuler un match récupéré
# ==============================
# Pour ce test, on ne récupère qu'un match fictif
match = {
    "team1": "Princeton Revolution",
    "team2": "New York Slice",
    "date": "2025-09-05T16:00:00",
    "venue": "ALAMEDA COUNTY FAIRGROUNDS"
}

# ==============================
# Ouvrir le fichier et écrire le match
# ==============================
with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
    # Chaque match écrit sur une ligne
    f.write(f"{match['team1']} vs {match['team2']}\n")

# ==============================
# Confirmation dans le log
# ==============================
print(f"[OK] Match écrit dans {OUTPUT_FILE}")