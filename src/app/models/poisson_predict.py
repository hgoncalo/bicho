import os
import sys
import pandas as pd
from pathlib import Path # Adicionado para melhor gestão de caminhos

# Configuração do Path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from app.data import utils
# poisson_extended está na mesma pasta (src/app/models/)
import poisson_extended

def predictMatch(team_a, team_b):
    last_season = utils.SEASONS[-1]
    if (utils.USED_MODEL == 'poisson_revamped'):
        filePath = utils.OUTPUT_PATH_REVAMPED / f"LF_{last_season}.csv"
    else:
        filePath = utils.OUTPUT_PATH
    df = pd.read_csv(filePath, index_col='Team')
    
    team_a_stats = df.loc[team_a]
    team_b_stats = df.loc[team_b]

    team_a_lambda_att = team_a_stats['LambdaAtt']
    team_a_lambda_def = team_a_stats['LambdaDef']
    team_a_hf = team_a_stats['HomeFactor']
    team_b_lambda_att = team_b_stats['LambdaAtt']
    team_b_lambda_def = team_b_stats['LambdaDef']
    return poisson_extended.betterPoissonStats(team_a_lambda_att * team_b_lambda_def * team_a_hf * utils.POISSON_OD, team_b_lambda_att * team_a_lambda_def * utils.POISSON_OD)

def predictMatchweek(games):
    for home_team, away_team in games:
        print("-------------------------------------")
        print(f"NEW MATCH: {home_team} VS {away_team}")
        predictMatch(home_team,away_team)
        print("-------------------------------------")
    return

if __name__ == "__main__":
    predictMatchweek(utils.GAMES_TO_PREDICT)