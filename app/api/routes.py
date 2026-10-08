from app.services import user_service
from flask import request, Flask, jsonify
from app.database import Session, Base, engine


Base.metadata.create_all(bind=engine)

app = Flask(__name__)


@app.route('/user/', methods=["POST"])
def create_user():
    data = request.get_json() or {}
    name = data.get("name")

    if not isinstance(name, str) or not name.strip():
        return jsonify({"error": "Name cannot be empty"}), 400

    session = Session()
    try:
        user = user_service.create_user(session, name)
        return jsonify({
            "id": user.id,
            "name": user.name
        }), 201
    except (KeyError, TypeError, ValueError) as error:
        return jsonify({"error": str(error)}), 400
    finally:
        session.close()


@app.route('/user/', methods=["DELETE"])
def delete_user():
    data = request.get_json() or {}
    user_id = data.get("id")

    if user_id is None:
        return jsonify({"error": "User id is required"}), 400

    session = Session()
    try:
        user_service.delete_user(session, user_id)
        return jsonify({"message": "User deleted successfully"}), 200
    except (KeyError, TypeError, ValueError) as error:
        return jsonify({"error": str(error)}), 400
    finally:
        session.close()


@app.route('/user/', methods=["GET"])
def list_users():
    session = Session()
    try:
        users = user_service.list_users(session)
        return jsonify([
            {"id": user.id, "name": user.name}
            for user in users
        ]), 200
    finally:
        session.close()


@app.route('/user/<int:user_id>', methods=["PUT", "PATCH"])
def update_user(user_id):
    data = request.get_json() or {}
    name = data.get("name")

    if not isinstance(name, str) or not name.strip():
        return jsonify({"error": "Name cannot be empty"}), 400

    session = Session()
    try:
        user = user_service.update_user(session, user_id, name)
        return jsonify({
            "id": user.id,
            "name": user.name
        }), 200
    except (KeyError, TypeError, ValueError) as error:
        return jsonify({"error": str(error)}), 400
    finally:
        session.close()