import json
from pathlib import Path
from flask import *

PROJECT_ROOT = Path(__file__).resolve().parent
JSON_FILE_PATH = PROJECT_ROOT / "matchweek_predictions.json"

app = Flask(__name__)
@app.route('/')
def root():
    return jsonify({
        'status' : "Online",
        'predictions': "Search /predictions to get the full list for the matchweek"
    })

@app.route('/predictions')
def get_predictions():
    try:
        with open(JSON_FILE_PATH,"r") as f:
            predictions = json.load(f)

    except FileNotFoundError:
        return abort(404, description="File not found. Have you executed the Bicho Pipeline?")
    except:
        return abort(500, description="Internal error.")
    
    # if there are queries (to find a specific game)
    home_query = request.args.get('home')
    away_query = request.args.get('away')
    team_query = request.args.get('team')
    if not home_query and not away_query and not team_query:
        return jsonify(predictions)
    
    queried_predictions = predictions
    if home_query:
        queried_predictions = [p for p in queried_predictions if (home_query.lower() == p['matchInfo']['homeTeam'].lower())]

    if away_query:
        queried_predictions = [p for p in queried_predictions if (away_query.lower() == p['matchInfo']['awayTeam'].lower())]
    
    if team_query:
        queried_predictions = [p for p in queried_predictions if (team_query.lower() == p['matchInfo']['homeTeam'].lower() or team_query.lower() == p['matchInfo']['awayTeam'].lower())]

    if not queried_predictions:
        return abort(404, description="No game found using your criteria")
    return jsonify(queried_predictions)

if __name__ == "__main__":
    app.run(debug=True,host="0.0.0.0",port=5000)