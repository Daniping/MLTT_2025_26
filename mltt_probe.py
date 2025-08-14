import requests
from bs4 import BeautifulSoup

MLTT_URL = "https://www.mltt.com/league/schedule"

def main():
    print(f"🔍 Lecture de la page : {MLTT_URL}")
    r = requests.get(MLTT_URL)
    r.raise_for_status()
    print("✅ Page téléchargée avec succès.")

    soup = BeautifulSoup(r.text, "html.parser")

    matches = soup.select(".upcoming-matches li")
    if not matches:
        print("⚠️ Aucun match trouvé avec le sélecteur .upcoming-matches li")
        return

    print(f"📅 {len(matches)} matchs trouvés :\n")
    for item in matches:
        text = item.get_text(separator=" ", strip=True)
        print(f" - {text}")

if __name__ == "__main__":
    main()

