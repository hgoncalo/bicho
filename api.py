import os
import json
from pathlib import Path
from flask import *
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import *
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent
JSON_FILE_PATH = PROJECT_ROOT / "matchweek_predictions.json"

app = Flask(__name__)

load_dotenv()
frontend_origin = os.getenv("ALLOWED_ORIGIN", "*")
CORS(app, resources={r"/*": {"origins": frontend_origin}})
app.config['SECRET_KEY'] = os.getenv("FLASK_SECRET_KEY")
app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", "sqlite:///bicho.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

bcrypt = Bcrypt(app)
jwt = JWTManager(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(16), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

@app.route('/')
def root():
    return jsonify({
        'status' : "Online",
        'predictions': "duh, it's online"
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

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password are required.'}), 400
    if len(username) < 4 or len(username) > 16:
        return jsonify({'error': 'Username must be between 4 and 16 characters.'}), 400
    if len(password) < 8 or len(password) > 24:
        return jsonify({'error': 'Password must be between 8 and 24 characters.'}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists.'}), 400
    
    hashed = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(username=username, password=hashed)
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'success': 'User registered successfully.'}), 201
    except:
        return jsonify({'error': 'Internal server error.'}), 500
    
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    user = User.query.filter_by(username=username).first()

    if not username or not password:
        return jsonify({'error': 'Username and password are required.'}), 400
    if not user or not bcrypt.check_password_hash(user.password, password):
        return jsonify({'error': 'Invalid username or password.'}), 401
    
    access_token = create_access_token(identity=user.id)
    return jsonify(
        {
            'access_token': access_token,
            'username': user.username
        }), 200
    
@app.route('/api/user', methods=['GET'])
@jwt_required()
def get_user():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({'error': 'User not found.'}), 404
    return jsonify({'id': user.id, 'username': user.username}), 200

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True,port=5000)