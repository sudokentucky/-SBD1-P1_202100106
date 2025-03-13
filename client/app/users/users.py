import bcrypt
import datetime
from utils.db import get_connection
from .db_users import *

def create_user(data):
    required_fields = ['username', 'email', 'password', 'national_document', 'name', 'lastname']
    if not all(field in data for field in required_fields):
        raise ValueError("Faltan campos requeridos")

    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    phone = data.get('phone')
    national_document = data.get('national_document')
    name = data.get('name')
    lastname = data.get('lastname')

    if len(password) < 6:
        raise ValueError("La contraseña debe tener al menos 6 caracteres")

    conn = get_connection()
    try:
        if is_username_taken(conn, username) or is_email_taken(conn, email):
            raise ValueError("El username o email ya existen")

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        created_at = datetime.datetime.now()

        client_id = insert_cliente(conn, national_document, name, lastname, username, phone, hashed_password, created_at)
        insert_email_cliente(conn, client_id, email, created_at)

        conn.commit()
        return client_id
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def add_address(data):
    username = data.get('username')
    address = data.get('address')
    if not username or not address:
        raise ValueError("Faltan el username o la dirección")

    conn = get_connection()
    try:
        user = get_client_by_username(conn, username)
        if not user:
            raise ValueError("Usuario no encontrado o inactivo")
        client_id = user[0]
        created_at = datetime.datetime.now()
        insert_address(conn, client_id, address, created_at)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def login_user(data):
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        raise ValueError("Faltan el username o la contraseña")

    conn = get_connection()
    try:
        user = get_client_by_username(conn, username)
        if not user:
            raise ValueError("Credenciales inválidas")
        user_id, stored_hash = user
        if not bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
            raise ValueError("Credenciales inválidas")
        session_id = f"Numero de Sesion{user_id}"
        return session_id
    finally:
        conn.close()

def get_user(user_id):
    conn = get_connection()
    try:
        user_row = get_client_by_id(conn, user_id)
        if not user_row:
            return None
        user = {
            "id": user_row[0],
            "username": user_row[1],
            "phone": user_row[2],
            "createdAt": user_row[3].isoformat() if user_row[3] else None
        }
        return user
    finally:
        conn.close()

def update_user(user_id, data):
    phone = data.get('phone')
    email = data.get('email')
    if not phone and not email:
        raise ValueError("No hay datos para actualizar")

    conn = get_connection()
    try:
        update_client(conn, user_id, phone, email)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def delete_user(user_id):
    conn = get_connection()
    try:
        delete_client(conn, user_id)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def get_clients_with_payment_methods():
    conn = get_connection()
    try:
        clients = list_clients_with_payment_methods(conn)
        return clients
    finally:
        conn.close()
