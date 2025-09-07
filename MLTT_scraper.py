# MLTT_scraper.py
OUTPUT_FILE = "MLTT_2025_26_V5.ics"

with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
    f.write("bonjour\n")

print(f"[OK] 'bonjour' ajouté dans {OUTPUT_FILE}")