import requests

API_URL = "https://web.mltt.com/api/schedule?seasonId=0e4e3575-5ac3-4afc-ba87-3930103569f0"
TEAM_NAME = "Florida Crocs"  # <-- mets ici le nom de l’équipe connue

def fetch_data():
    response = requests.get(API_URL)
    response.raise_for_status()
    return response.json()

# Recherche récursive du nom d'équipe
def search_team(obj, team_name, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            new_path = f"{path}/{k}"
            if isinstance(v, (dict, list)):
                yield from search_team(v, team_name, new_path)
            elif isinstance(v, str) and team_name.lower() in v.lower():
                yield new_path, v
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            new_path = f"{path}[{i}]"
            yield from search_team(v, team_name, new_path)

def main():
    data = fetch_data()
    found = list(search_team(data, TEAM_NAME))
    if found:
        print(f"Occurrences de '{TEAM_NAME}' trouvées :")
        for path, value in found:
            print(f" - Chemin: {path} | Valeur: {value}")
    else:
        print(f"Aucune occurrence de '{TEAM_NAME}' trouvée dans les données.")

if __name__ == "__main__":
    main()
