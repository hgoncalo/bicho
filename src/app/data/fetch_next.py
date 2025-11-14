import requests
from bs4 import BeautifulSoup
from . import utils

def transformNames(teams):
    real_teams = []
    for team in teams:
        if team == "Vitória SC": rt = "Guimaraes"
        elif team == "AFS": rt = "AVS"
        elif team == "Casa Pia AC": rt = "Casa Pia"
        elif team == "FC Alverca": rt = "Alverca"
        elif team == "FC Famalicão": rt = "Famalicao"
        elif team == "CD Tondela": rt = "Tondela"
        elif team == "Sporting": rt = "Sp Lisbon"
        elif team == "Est. Amadora": rt = "Estrela"
        elif team == "FC Porto": rt = "Porto"
        elif team == "Estoril Praia": rt = "Estoril"
        elif team == "FC Arouca": rt = "Arouca"
        elif team == "SC Braga": rt = "Sp Braga"
        else: rt = team
        real_teams.append(rt)
    return real_teams

# its only working for zerozero!
def fetchNextMatchweek():
    try:
        matchweek = []
        response = requests.get(utils.LEAGUE_AGENDA_URL,headers=utils.WEB_HEADERS)
        fs_html = response.text
        soup = BeautifulSoup(fs_html, 'html.parser')
        sp = soup.select(".box > #fixture_games")
        next_fixture = sp[1]
        fixture_list = next_fixture.find_all("tr")

        for f in fixture_list:
            teams = [t.get_text(strip=True) for t in f.select(".text > a")]
            real_teams = transformNames(teams)
            home_team = real_teams[0]
            away_team = real_teams[1]
            matchday = (home_team,away_team)
            matchweek.append(matchday)
        return matchweek
    except:
        return 1

if __name__ == "__main__":
    fetchNextMatchweek()