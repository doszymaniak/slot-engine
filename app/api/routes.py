from app.services import user_service, resource_service, reservation_service
from flask import request, Flask, jsonify
from app.database import Session

app = Flask(__name__)


# USER API
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


# RESOURCE API
@app.route('/resource/', methods=["POST"])
def create_resource():
    data = request.get_json() or {}
    name = data.get("name")

    if not isinstance(name, str) or not name.strip():
        return jsonify({"error": "Name cannot be empty"}), 400

    session = Session()
    try:
        resource = resource_service.create_resource(session, name)
        return jsonify({
            "id": resource.id,
            "name": resource.name
        }), 201
    except (KeyError, TypeError, ValueError) as error:
        return jsonify({"error": str(error)}), 400
    finally:
        session.close()


@app.route('/resource/', methods=["DELETE"])
def delete_resource():
    data = request.get_json() or {}
    resource_id = data.get("id")

    if resource_id is None:
        return jsonify({"error": "Resource id is required"}), 400

    session = Session()
    try:
        resource_service.delete_resource(session, resource_id)
        return jsonify({"message": "Resource deleted successfully"}), 200
    except (KeyError, TypeError, ValueError) as error:
        return jsonify({"error": str(error)}), 400
    finally:
        session.close()


@app.route('/resource/', methods=["GET"])
def list_resources():
    session = Session()
    try:
        resources = resource_service.list_resources(session)
        return jsonify([
            {"id": resource.id, "name": resource.name}
            for resource in resources
        ]), 200
    finally:
        session.close()


@app.route('/resource/<int:resource_id>', methods=["PUT", "PATCH"])
def update_resource(resource_id):
    data = request.get_json() or {}
    name = data.get("name")

    if not isinstance(name, str) or not name.strip():
        return jsonify({"error": "Name cannot be empty"}), 400

    session = Session()
    try:
        resource = resource_service.update_resource(session, resource_id, name)
        return jsonify({
            "id": resource.id,
            "name": resource.name
        }), 200
    except (KeyError, TypeError, ValueError) as error:
        return jsonify({"error": str(error)}), 400
    finally:
        session.close()


# RESERVATION API
@app.route('/reservation/', methods=["POST"])
def create_reservation():
    data = request.get_json() or {}
    user_id = data.get("user_id")
    resource_id = data.get("resource_id")
    
    start = data.get("start")
    end = data.get("end")

    if user_id is None:
        return jsonify({"error": "User id is required"}), 400

    if resource_id is None:
        return jsonify({"error": "Resource id is required"}), 400

    if start is None:
        return jsonify({"error": "Start date is required"}), 400

    if end is None:
        return jsonify({"error": "End date is required"}), 400

    try:
        start = reservation_service.convert_string_to_date(start)
        end = reservation_service.convert_string_to_date(end)
    except (TypeError, ValueError):
        return jsonify({
            "error": "Start and end must use YYYY-MM-DD HH:MM:SS format"
        }), 400

    session = Session()
    try:
        reservation = reservation_service.create_reservation(session, user_id, resource_id, start, end)
        return jsonify({
            "id": reservation.id,
            "user_id": reservation.user_id,
            "resource_id": reservation.resource_id,
            "start": reservation.start,
            "end": reservation.end
        }), 201
    except (KeyError, TypeError, ValueError) as error:
        return jsonify({"error": str(error)}), 400
    finally:
        session.close()


@app.route('/reservation/', methods=["DELETE"])
def delete_reservation():
    data = request.get_json() or {}

    reservation_id = data.get("reservation_id")

    if reservation_id is None:
        return jsonify({"error": "Reservation id is required"}), 400

    session = Session()
    try:
        reservation_service.delete_reservation(session, reservation_id)
        return jsonify({"message": "Reservation deleted successfully"}), 200
    except (KeyError, TypeError, ValueError) as error:
        return jsonify({"error": str(error)}), 400
    finally:
        session.close()


@app.route('/reservation/', methods=["GET"])
def list_reservations():
    session = Session()
    try:
        reservations = reservation_service.list_reservations(session)
        return jsonify([{
            "id": reservation.id,
            "user_id": reservation.user_id,
            "resource_id": reservation.resource_id,
            "start": reservation.start,
            "end": reservation.end
        } for reservation in reservations]), 200
    finally:
        session.close()


@app.route('/reservation/<int:reservation_id>', methods=["PUT", "PATCH"])
def update_reservation(reservation_id):
    data = request.get_json() or {}

    start = data.get("start")
    end = data.get("end")

    if start is None:
        return jsonify({"error": "Start date is required"}), 400

    if end is None:
        return jsonify({"error": "End date is required"}), 400

    try:
        start = reservation_service.convert_string_to_date(start)
        end = reservation_service.convert_string_to_date(end)
    except (TypeError, ValueError):
        return jsonify({
            "error": "Start and end must use YYYY-MM-DD HH:MM:SS format"
        }), 400

    session = Session()
    try:
        reservation = reservation_service.update_reservation(session, reservation_id, start, end)
        return jsonify({
            "id": reservation.id,
            "user_id": reservation.user_id,
            "resource_id": reservation.resource_id,
            "start": reservation.start,
            "end": reservation.end
        }), 200
    except (KeyError, TypeError, ValueError) as error:
        return jsonify({"error": str(error)}), 400
    finally:
        session.close()