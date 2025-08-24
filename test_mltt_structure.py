import requests

API_URL = "https://web.mltt.com/api/schedule?seasonId=0e4e3575-5ac3-4afc-ba87-3930103569f0"

def fetch_dhle():
    response = requests.get(API_URL)
    response.raise_for_status()
    return response.json()

def list_keys(data, path=""):
    keys = set()
    if isinstance(data, dict):
        for k, v in data.items():
            keys.add(path + k)
            keys.update(list_keys(v, path + k + "."))
    elif isinstance(data, list):
        for i, item in enumerate(data):
            keys.update(list_keys(item, path + f"[{i}]."))
    return keys

def main():
    data = fetch_dhle()
    keys = list_keys(data)
    print("Clés uniques dans le JSON :")
    for k in sorted(keys):
        print(k)

if __name__ == "__main__":
    main()
