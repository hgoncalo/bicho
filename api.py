import os
import json
from flask import *
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import *
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)

frontend_origin = os.getenv("ALLOWED_ORIGIN", "*")
CORS(app, resources={r"/*": {"origins": frontend_origin}})
app.config['SECRET_KEY'] = os.getenv("FLASK_SECRET_KEY")
app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db_url = os.getenv('DATABASE_URL', 'sqlite:///instance/bicho.db')
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)
    
app.config['SQLALCHEMY_DATABASE_URI'] = db_url

bcrypt = Bcrypt(app)
jwt = JWTManager(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(16), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

class Prediction(db.Model):
    __tablename__ = 'predictions' 
    id = db.Column(db.Integer, primary_key=True)
    home_team = db.Column(db.String(50), nullable=False)
    away_team = db.Column(db.String(50), nullable=False)
    data_json = db.Column(db.Text, nullable=False)

    def to_dict(self):
        try:
            return json.loads(self.data_json)
        except json.JSONDecodeError:
            return {
                "id": self.id, 
                "matchInfo": {"homeTeam": self.home_team, "awayTeam": self.away_team},
                "error": "JSON Decode Error"
            }
        
@app.route('/')
def root():
    return jsonify({
        'status' : "Online",
        'predictions': "duh, it's online"
    })

@app.route('/predictions')
def get_predictions():
    try:
        all_predictions_objects = db.session.execute(
            db.select(Prediction).order_by(Prediction.id)
        ).scalars().all()

        predictions = [p.to_dict() for p in all_predictions_objects]

    except Exception as e:
        print(f"Database error: {e}")
        return jsonify({'error': 'Internal server error reading predictions from database.'}), 500
    
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