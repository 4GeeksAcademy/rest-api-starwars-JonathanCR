"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for, send_from_directory
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from src.utils import APIException, generate_sitemap
from src.admin import setup_admin
from src.models import db, User, Planet, People, Favorite

ENV = os.getenv("FLASK_ENV")
static_file_dir = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), '../public/')
app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db, compare_type=True)
db.init_app(app)
CORS(app)
setup_admin(app)


@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code


@app.route('/')
def sitemap():
    if ENV == "development":
        return generate_sitemap(app)
    return send_from_directory(static_file_dir, 'index.html')


@app.route('/people', methods=['GET'])
def get_all_people():
    all_people = People.query.all()
    if not all_people:
        return jsonify({"message": "No people found"}), 404

    serialized_people = [person.serialize() for person in all_people]
    return jsonify(serialized_people), 200


@app.route('/people/<int:people_id>', methods=['GET'])
def get_single_person(people_id):
    person = People.query.get(people_id)
    if not person:
        return jsonify({"message": "Person not found"}), 404
    return jsonify(person.serialize()), 200


@app.route('/planets', methods=['GET'])
def get_all_planets():
    all_planets = Planet.query.all()
    if not all_planets:
        return jsonify({"message": "No planets found"}), 404

    serialized_planets = [planet.serialize() for planet in all_planets]
    return jsonify(serialized_planets), 200


@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_single_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if not planet:
        return jsonify({"message": "Planet not found"}), 404
    return jsonify(planet.serialize()), 200


@app.route('/users', methods=['GET'])
def get_all_users():
    all_users = User.query.all()
    if not all_users:
        return jsonify({"message": "No users found"}), 404

    serialized_users = [user.serialize() for user in all_users]
    return jsonify(serialized_users), 200


@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    user_id_to_check = 1

    user = User.query.get(user_id_to_check)
    if not user:
        return jsonify({"message": "User not found or no authentication"}), 404

    favorites = [fav.serialize() for fav in user.favorites]

    if not favorites:
        return jsonify({"message": "User has no favorites yet"}), 200

    return jsonify(favorites), 200


@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    user_id = 1

    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    planet = Planet.query.get(planet_id)
    if not planet:
        return jsonify({"message": "Planet not found"}), 404

    existing_favorite = Favorite.query.filter_by(
        user_id=user_id, planet_id=planet_id).first()
    if existing_favorite:
        return jsonify({"message": "Planet already in favorites"}), 409

    new_favorite = Favorite(
        user_id=user_id, planet_id=planet_id, people_id=None)

    try:
        db.session.add(new_favorite)
        db.session.commit()
        return jsonify({"message": "Planet added to favorites successfully", "favorite": new_favorite.serialize()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error adding planet to favorites", "error": str(e)}), 500


@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_person(people_id):
    user_id = 1

    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    person = People.query.get(people_id)
    if not person:
        return jsonify({"message": "Person not found"}), 404

    existing_favorite = Favorite.query.filter_by(
        user_id=user_id, people_id=people_id).first()
    if existing_favorite:
        return jsonify({"message": "Person already in favorites"}), 409

    new_favorite = Favorite(
        user_id=user_id, people_id=people_id, planet_id=None)

    try:
        db.session.add(new_favorite)
        db.session.commit()
        return jsonify({"message": "Person added to favorites successfully", "favorite": new_favorite.serialize()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error adding person to favorites", "error": str(e)}), 500


@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    user_id = 1

    favorite_to_delete = Favorite.query.filter_by(
        user_id=user_id, planet_id=planet_id).first()

    if not favorite_to_delete:
        return jsonify({"message": "Favorite planet not found for this user"}), 404

    try:
        db.session.delete(favorite_to_delete)
        db.session.commit()
        return jsonify({"message": "Favorite planet deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error deleting favorite planet", "error": str(e)}), 500


@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_person(people_id):
    user_id = 1

    favorite_to_delete = Favorite.query.filter_by(
        user_id=user_id, people_id=people_id).first()

    if not favorite_to_delete:
        return jsonify({"message": "Favorite person not found for this user"}), 404

    try:
        db.session.delete(favorite_to_delete)
        db.session.commit()
        return jsonify({"message": "Favorite person deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error deleting favorite person", "error": str(e)}), 500


if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=True)
