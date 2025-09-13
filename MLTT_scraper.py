# ===========================================
# MLTT_scraper.py - Scraper MLTT finalisé
# BLOC IMPÉRATIF (à ne jamais modifier une fois validé)
# - Installe les dépendances si nécessaire
# - Vide le fichier du repo
# - Initialise des fonctions critiques
# ===========================================

import os
import sys
import subprocess

OUTPUT_FILE = "MLTT_2025_26_V5.ics"

def ensure_requirements():
    """Installe automatiquement les dépendances manquantes"""
    try:
        import requests
        import bs4
        import playwright
    except ImportError:
        print("[SETUP] Installation des dépendances manquantes...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "beautifulsoup4", "playwright"])
        subprocess.check_call([sys.executable, "-m", "playwright", "install"])

def clear_output_file():
    """Vide le fichier de sortie"""
    open(OUTPUT_FILE, "w", encoding="utf-8").close()
    print(f"[SETUP] {OUTPUT_FILE} vidé.")

# Exécution impérative au démarrage
ensure_requirements()
clear_output_file()

# ===========================================
# FIN DU BLOC IMPÉRATIF
# Tout le reste peut être modifié librement
# ===========================================

import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

def fetch_teams():
    """Scrape la liste officielle des équipes depuis https://mltt.com/teams"""
    url = "https://mltt.com/teams"
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    teams = [h2.get_text(strip=True) for h2 in soup.find_all("h2") if h2.get_text(strip=True)]
    print(f"[OK] {len(teams)} équipes trouvées via scraping.")
    return teams

def fetch_matches():
    """Scrape la page des matchs et récupère les équipes via ALT des logos"""
    url = "https://mltt.com/league/schedule"
    matches = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)
        page.wait_for_timeout(5000)
        match_blocks = page.query_selector_all("div.future-match-single-top-wrap")
        for block in match_blocks:
            team_imgs = block.query_selector_all("div.schedule-team-logo img")
            teams = []
            for img in team_imgs:
                alt = img.get_attribute("alt") or "?"
                teams.append(alt)
            if len(teams) >= 2:
                matches.append((teams[0], teams[1]))
        browser.close()
    return matches

if __name__ == "__main__":
    # 1. récupérer la liste des équipes
    all_teams = fetch_teams()

    # 2. récupérer tous les matchs
    matches = fetch_matches()

    # 3. supprimer les doublons tout en conservant l'ordre
    seen, unique_matches = set(), []
    for t1, t2 in matches:
        key = (t1, t2)
        if key not in seen:
            seen.add(key)
            unique_matches.append(key)

    # 4. écrire les équipes + matchs dans le fichier
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        f.write("Équipes officielles MLTT :\n")
        for team in all_teams:
            f.write(f"- {team}\n")
        f.write("\nMatchs à venir :\n")
        for t1, t2 in unique_matches:
            f.write(f"{t1} vs {t2}\n")

    print(f"[OK] {len(unique_matches)} matchs uniques écrits dans {OUTPUT_FILE}")