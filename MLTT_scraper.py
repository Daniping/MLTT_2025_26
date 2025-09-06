# write_hello.py

FILE_PATH = "MLTT_2025_26_V5.ics"

with open(FILE_PATH, "w", encoding="utf-8") as f:
    f.write("bonjour\n")

print(f"[OK] Écriture terminée dans {FILE_PATH}")