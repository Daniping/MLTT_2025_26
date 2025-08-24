import requests

API_URL = "https://web.mltt.com/api/schedule?seasonId=0e4e3575-5ac3-4afc-ba87-3930103569f0"

def fetch_dhle():
    response = requests.get(API_URL)
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
        if keyword.lower() in str(data).lower():  # insensible à la casse
            results.append((path, data))
    return results

def main():
    matches = fetch_dhle()
    keyword = "crocs"   # 🔍 cherche partout le mot "crocs"
    results = search_keyword(matches, keyword)

    if results:
        print(f"Occurrences de '{keyword}' trouvées :")
        for path, value in results:
            print(f"{path} -> {value}")
    else:
        print(f"Aucune occurrence de '{keyword}' trouvée.")

if __name__ == "__main__":
    main()
