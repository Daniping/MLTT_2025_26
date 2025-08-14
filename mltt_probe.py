import requests
from bs4 import BeautifulSoup

URL = "https://www.mltt.com/league/schedule"

def fetch_matches():
    response = requests.get(URL)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    matches = []
    for match in soup.select("h3 + div.match"):
        date = match.find("p", class_="date").get_text(strip=True)
        time = match.find("p", class_="time").get_text(strip=True)
        location = match.find("p", class_="location").get_text(strip=True)
        matches.append(f"{date} {time} - {location}")

    return matches

if __name__ == "__main__":
    matches = fetch_matches()
    if matches:
        print("📅 Matchs trouvés :")
        for match in matches:
            print(match)
    else:
        print("⚠️ Aucun match trouvé")

