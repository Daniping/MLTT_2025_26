# MLTT_scraper.py
# Test simple : écrire "bonjour" dans MLTT_2025_26_V5.ics

ICS_FILE = "MLTT_2025_26_V5.ics"

with open(ICS_FILE, "a", encoding="utf-8") as f:
    f.write("bonjour\n")

print(f"[OK] 'bonjour' ajouté dans {ICS_FILE}")