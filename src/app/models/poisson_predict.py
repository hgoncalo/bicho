import os
import sys
import pandas as pd

# Configuração do Path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from app.data import fetch_next,utils
from . import poisson_extended

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

def predictMatchweek():
    games = fetch_next.fetchNextMatchweek()
    match_predictions = []

    for home_team, away_team in games:
        prediction = dict()
        prediction['matchInfo'] = {
            "homeTeam" : home_team,
            "awayTeam" : away_team
        }
        prediction['matchPredictions'] = predictMatch(home_team,away_team)
        match_predictions.append(prediction)
    return match_predictions

if __name__ == "__main__":
    predictMatchweek()