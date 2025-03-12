from flask import Blueprint, request, jsonify
import bcrypt
import datetime
from utils.db import get_connection

users_bp = Blueprint('users', __name__, url_prefix='/api/users')

@users_bp.route('', methods=['POST'])
def create_user():
    data = request.get_json()

    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    phone = data.get('phone')
    national_document = data.get('national_document')
    name = data.get('name')
    lastname = data.get('lastname')

    if not all([username, email, password, national_document, name, lastname]):
        return jsonify({"status": "error", "message": "Missing required fields"}), 400

    if len(password) < 6:
        return jsonify({"status": "error", "message": "Password must be at least 6 characters"}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM CLIENTE WHERE username = :username", {'username': username})
        username_exists = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM EMAILCLIENTE WHERE email = :email", {'email': email})
        email_exists = cursor.fetchone()[0]

        if username_exists or email_exists:
            return jsonify({
                "status": "error",
                "message": "Username or email already exists"
            }), 409

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        created_at = datetime.datetime.now()

        insert_cliente_sql = """
            INSERT INTO CLIENTE (
                id, national_document, name, lastname, username, phone, active, password, created_at, updated_at
            )
            VALUES (
                CLIENTE_SEQ.NEXTVAL, :national_document, :name, :lastname, :username, :phone, :active, :password, :created_at, :created_at
            )
        """
        cursor.execute(insert_cliente_sql, {
            'national_document': national_document,
            'name': name,
            'lastname': lastname,
            'username': username,
            'phone': phone,
            'active': 1,  
            'password': hashed_password,
            'created_at': created_at
        })

        cursor.execute("SELECT CLIENTE_SEQ.CURRVAL FROM dual")
        cliente_id = cursor.fetchone()[0]

        insert_email_sql = """
            INSERT INTO EMAILCLIENTE (
                id, client_id, email, confirmed, created_at, updated_at
            )
            VALUES (
                EMAILCLIENTE_SEQ.NEXTVAL, :client_id, :email, :confirmed, :created_at, :created_at
            )
        """
        cursor.execute(insert_email_sql, {
            'client_id': cliente_id,
            'email': email,
            'confirmed': 1, 
            'created_at': created_at
        })

        conn.commit()

        return jsonify({
            "status": "success",
            "message": "User created successfully",
            "user_id": cliente_id
        }), 201

    except Exception as e:
        conn.rollback()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

    finally:
        cursor.close()
        conn.close()

@users_bp.route('/add_address', methods=['POST'])
def add_address():
    data = request.get_json()
    #valido mis campos
    username = data.get('username')
    address = data.get('address')

    if not username or not address:
        return jsonify({"status": "error", "message": "Missing username or address"}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = "SELECT id FROM CLIENTE WHERE username = :username AND active = 1"
        cursor.execute(query, {'username': username})
        row = cursor.fetchone()

        if not row:
            return jsonify({"status": "error", "message": "User not found or inactive"}), 404

        client_id = row[0]
        created_at = datetime.datetime.now()
        insert_direccion_sql = """
            INSERT INTO DIRECCION (
                id, client_id, address, created_at, updated_at
            )
            VALUES (
                DIRECCION_SEQ.NEXTVAL, :client_id, :address, :created_at, :created_at
            )
        """
        cursor.execute(insert_direccion_sql, {
            'client_id': client_id,
            'address': address,
            'created_at': created_at
        })

        conn.commit()

        return jsonify({
            "status": "success",
            "message": f"Address added for user '{username}'"
        }), 201

    except Exception as e:
        conn.rollback()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

    finally:
        cursor.close()
        conn.close()


@users_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({"status": "error", "message": "Missing username or password"}), 400

    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT id, password FROM CLIENTE WHERE username = :username"
    cursor.execute(query, username=username)
    row = cursor.fetchone()
    cursor.close()
    if row is None:
        return jsonify({"status": "error", "message": "Invalid credentials"}), 401

    user_id, stored_hash = row
    if not bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
        return jsonify({"status": "error", "message": "Invalid credentials"}), 401

    session_id = f"Numero de Sesion{user_id}"
    return jsonify({"status": "success", "message": "User authenticated", "sessionId": session_id}), 200

@users_bp.route('/<int:id>', methods=['GET'])
def get_user(id):
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT id, username, phone, created_at FROM CLIENTE WHERE id = :id"
    cursor.execute(query, id=id)
    row = cursor.fetchone()
    cursor.close()
    if row is None:
        return jsonify({"status": "error", "message": "User not found"}), 404

    user = {
        "id": row[0],
        "username": row[1],
        "phone": row[2],
        "createdAt": row[3].isoformat() if row[3] else None
    }
    return jsonify(user), 200

@users_bp.route('/<int:id>', methods=['PUT'])
def update_user(id):
    data = request.get_json()
    phone = data.get('phone')
    email = data.get('email')
    if not phone and not email:
        return jsonify({"status": "error", "message": "Nothing to update"}), 400

    conn = get_connection()
    cursor = conn.cursor()
    update_fields = []
    params = {"id": id}
    if phone:
        update_fields.append("phone = :phone")
        params["phone"] = phone
    if email:
        update_fields.append("email = :email")
        params["email"] = email
    update_sql = "UPDATE CLIENTE SET " + ", ".join(update_fields) + " WHERE id = :id"
    cursor.execute(update_sql, params)
    conn.commit()
    cursor.close()
    return jsonify({"status": "success", "message": "User updated successfully"}), 200

@users_bp.route('/<int:id>', methods=['DELETE'])
def delete_user(id):
    conn = get_connection()
    cursor = conn.cursor()
    update_sql = "UPDATE CLIENTE SET active = 0 WHERE id = :id"
    cursor.execute(update_sql, id=id)
    conn.commit()
    cursor.close()
    return jsonify({"status": "success", "message": "User deleted/inactivated successfully"}), 200