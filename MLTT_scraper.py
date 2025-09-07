# MLTT_scraper.py
# Test simple d'écriture forcée dans MLTT_2025_26_V5.ics

def save_test_message(filename="MLTT_2025_26_V5.ics"):
    with open(filename, "a", encoding="utf-8") as f:
        f.write("TEST MATCH 1 vs TEST MATCH 2\n")
    print(f"[OK] Message écrit dans {filename}")

if __name__ == "__main__":
    save_test_message()