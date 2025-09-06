# MLTT_scraper.py - test écriture

OUTPUT_FILE = "MLTT_2025_26_V5.ics"

with open(OUTPUT_FILE, "a", encoding="utf-8") as f:  # "a" pour ajouter à la fin
    f.write("bonjour\n")

print(f"[OK] 'bonjour' écrit dans {OUTPUT_FILE}")