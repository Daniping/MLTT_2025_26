import requests

BASE_URL = "https://web.mltt.com/api"
SEASON_ID = "0e4e3575-5ac3-4afc-ba87-3930103569f0"
TEAM_NAME = "Florida Crocs"  # ou autre équipe que tu veux chercher

# Endpoints à tester
endpoints = [
    f"/schedule?seasonId={SEASON_ID}",
    f"/matches?seasonId={SEASON_ID}",
    f"/events?seasonId={SEASON_ID}",
    f"/tournaments?seasonId={SEASON_ID}"
]

def fetch_data(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def search_keyword(data, keyword, path=""):
    results = []
    if isinstance(data, dict):
        for k, v in data.items():
            results.extend(search_keyword(v, keyword, path + f".{k}"))
    elif isinstance(data, list):
        for i, item in enumerate(data):
            results.extend(search_keyword(item, keyword, path + f"[{i}]"))
    else:
        if keyword.lower() in str(data).lower():
            results.append((path, data))
    return results

def main():
    found_any = False
    for ep in endpoints:
        url = BASE_URL + ep
        print(f"\nTest de l'endpoint : {url}")
        try:
            data = fetch_data(url)
        except Exception as e:
            print(f"Erreur lors de l'accès : {e}")
            continue

        results = search_keyword(data, TEAM_NAME)
        if results:
            found_any = True
            print(f"Occurrences de '{TEAM_NAME}' trouvées :")
            for path, value in results:
                print(f"{path} -> {value}")
        else:
            print(f"Aucune occurrence de '{TEAM_NAME}' trouvée sur cet endpoint.")

    if not found_any:
        print("\nAucune occurrence trouvée sur tous les endpoints testés.")

if __name__ == "__main__":
    main()
