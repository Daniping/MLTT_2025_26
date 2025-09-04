import requests
from bs4 import BeautifulSoup

URL = "https://mltt.com/league/schedule"
resp = requests.get(URL)
resp.raise_for_status()

soup = BeautifulSoup(resp.text, "html.parser")

# Trouver tous les blocs de matchs
match_blocks = soup.select(".future-match-single-wrap")  # ou autre classe si différente

for i, block in enumerate(match_blocks, start=1):
    print(f"\n--- Match {i} ---")
    print(block.prettify()[:500])  # affiche les 500 premiers caractères du HTML du match
