# this file is a complete pipeline to run simulations
# doesen't include poisson_extended calls
import requests
import sys
import json
import os
from os import path
from pathlib import Path

project_root = Path(__file__).resolve().parent 
src_app_path = project_root / 'src' / 'app'
sys.path.append(str(src_app_path))

from api import app, db, Prediction 

from data import utils
from data import clean_data
from models import poisson,poisson_revamped, poisson_predict

# -1 if doesen't exist, 0 if dirty, 1 if clean
def fileExists(file_name):
    if (path.isfile(utils.DIRTY_PATH / f"{file_name}.csv")):
        return 0
    return -1

def extractSeason(cur_season):
    cb = fileExists(cur_season)
    if (cb < 0 or (cur_season == utils.SEASONS[-1])): 
        season_id = cur_season.replace('_','')
        season_url = f"https://www.football-data.co.uk/mmz4281/{season_id}/{utils.LEAGUE_ID}.csv"
        try:
            response = requests.get(season_url)
            response.raise_for_status()
            filePath = utils.DIRTY_PATH / f"{cur_season}.csv"
            with open(filePath, "wb") as f:
                f.write(response.content)
        except:
            return 1 
    return 0

def fetchSeasons():
    for s in utils.SEASONS:
        if (extractSeason(s) == 1):
            return 1
    clean_data.getData()
    return 0

def save_predictions_to_db(predictions_list):
    with app.app_context():
        try:
            db.session.query(Prediction).delete()
        
            new_predictions = []
            for p in predictions_list:
                home = p['matchInfo']['homeTeam']
                away = p['matchInfo']['awayTeam']
                data_json = json.dumps(p)
                
                new_prediction = Prediction(
                    home_team=home,
                    away_team=away,
                    data_json=data_json
                )
                new_predictions.append(new_prediction)
            
            db.session.add_all(new_predictions)
            db.session.commit()
            return 0
        except Exception as e:
            db.session.rollback()
            print(f"Error updating DB: {e}")
            return 1

def main():
    if (fetchSeasons() == 1):
        return 1
    else:
        if (utils.USED_MODEL == 'poisson_revamped'):
            poisson_revamped.start()
        else:
            poisson.start()
        output = poisson_predict.predictMatchweek()

        if output:
            if (save_predictions_to_db(output) == 1):
                return 1
    return 0

if __name__ == '__main__':
    if main() != 0:
        sys.exit(1)