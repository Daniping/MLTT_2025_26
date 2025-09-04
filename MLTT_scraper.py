from bs4 import BeautifulSoup
from datetime import datetime
import pytz

# Supposons que 'html_content' contient ton HTML récupéré avec Playwright ou requests
soup = BeautifulSoup(html_content, "html.parser")

matches = []

# Chaque match est dans un bloc 'future-match-single-top-wrap'
for match_block in soup.select(".future-match-single-top-wrap"):
    team_divs = match_block.select(".future-match-single-details-wrap .schedule-team-logo div")
    
    if len(team_divs) >= 2:
        team1 = team_divs[0].get_text(strip=True)
        team2 = team_divs[1].get_text(strip=True)
        
        # Récupérer date et lieu si nécessaire
        date_div = match_block.select_one(".future-match-game-title")
        venue_div = match_block.select_one(".future-match-game-title.mb-0")
        
        date_str = date_div.get_text(strip=True) if date_div else "Unknown date"
        venue = venue_div.get_text(strip=True) if venue_div else "Unknown venue"

        matches.append({
            "team1": team1,
            "team2": team2,
            "date": date_str,
            "venue": venue
        })
    else:
        print("Erreur parsing match: équipes manquantes")

# Vérifions le résultat
for m in matches:
    print(m)