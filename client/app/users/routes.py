from flask import Blueprint, request, jsonify
from .users import *

users_bp = Blueprint('users', __name__, url_prefix='/api/users')

@users_bp.route('', methods=['POST'])
def create_user_route():
    try:
        data = request.get_json()
        user_id = create_user(data)
        return jsonify({
            "status": "success",
            "message": "Usuario creado correctamente",
            "user_id": user_id
        }), 201
    except ValueError as ve:
        return jsonify({"status": "error", "message": str(ve)}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@users_bp.route('/add_address', methods=['POST'])
def add_address_route():
    try:
        data = request.get_json()
        add_address(data)
        return jsonify({
            "status": "success",
            "message": "Dirección agregada correctamente"
        }), 201
    except ValueError as ve:
        return jsonify({"status": "error", "message": str(ve)}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@users_bp.route('/login', methods=['POST'])
def login_route():
    try:
        data = request.get_json()
        session_id = login_user(data)
        return jsonify({
            "status": "success",
            "message": "Usuario autenticado",
            "sessionId": session_id
        }), 200
    except ValueError as ve:
        return jsonify({"status": "error", "message": str(ve)}), 401
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@users_bp.route('/<int:id>', methods=['GET'])
def get_user_route(id):
    try:
        user = get_user(id)
        if not user:
            return jsonify({"status": "error", "message": "Usuario no encontrado"}), 404
        return jsonify(user), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@users_bp.route('/<int:id>', methods=['PUT'])
def update_user_route(id):
    try:
        data = request.get_json()
        update_user(id, data)
        return jsonify({"status": "success", "message": "Usuario actualizado correctamente"}), 200
    except ValueError as ve:
        return jsonify({"status": "error", "message": str(ve)}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@users_bp.route('/<int:id>', methods=['DELETE'])
def delete_user_route(id):
    try:
        delete_user(id)
        return jsonify({"status": "success", "message": "Usuario inactivado correctamente"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@users_bp.route('/payment_methods', methods=['GET'])
def list_clients_with_payment_methods_route():
    try:
        clients = get_clients_with_payment_methods()
        return jsonify({"clients": clients}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
