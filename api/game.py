from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///players.db'  # SQLite database file named players.db
db = SQLAlchemy(app)
api = Api(app)

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    game_points = db.Column(db.Integer, nullable=False)

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "game_points": self.game_points
        }

class PlayerListResource(Resource):
    def get(self):
        players = Player.query.all()
        return jsonify([player.serialize() for player in players])
    
    def post(self):
        data = request.get_json()
        name = data['name']
        game_points = data['game_points']
        
        # Check if the player with the given name already exists
        existing_player = Player.query.filter_by(name=name).first()
        
        if existing_player:
            # If the player exists, update their game points
            existing_player.game_points += game_points
            db.session.commit()
            return jsonify(existing_player.serialize())
        else:
            # If the player does not exist, create a new player
            new_player = Player(name=name, game_points=game_points)
            db.session.add(new_player)
            db.session.commit()
            return jsonify(new_player.serialize())

class PlayerResource(Resource):
    def delete(self, player_id):
        player = Player.query.get_or_404(player_id)
        db.session.delete(player)
        db.session.commit()
        return '', 204

api.add_resource(PlayerListResource, '/players')
api.add_resource(PlayerResource, '/players/<int:player_id>')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=8085, debug=True)
