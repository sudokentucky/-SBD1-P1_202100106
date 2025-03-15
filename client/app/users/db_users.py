
def is_username_taken(conn, username):
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT COUNT(*) FROM CLIENTE WHERE username = :username", 
            {'username': username}
        )
        return cursor.fetchone()[0] > 0
    finally:
        cursor.close()

def is_email_taken(conn, email):
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT COUNT(*) FROM EMAILCLIENTE WHERE email = :email", 
            {'email': email}
        )
        return cursor.fetchone()[0] > 0
    finally:
        cursor.close()

def insert_cliente(conn, national_document, name, lastname, username, phone, hashed_password, created_at):
    cursor = conn.cursor()
    try:
        insert_sql = """
            INSERT INTO CLIENTE (
                id, national_document, name, lastname, username, phone, active, password, created_at, updated_at
            )
            VALUES (
                CLIENTE_SEQ.NEXTVAL, :national_document, :name, :lastname, :username, :phone, :active, :password, :created_at, :created_at
            )
        """
        cursor.execute(insert_sql, {
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
        client_id = cursor.fetchone()[0]
        return client_id
    finally:
        cursor.close()

def insert_email_cliente(conn, client_id, email, created_at, confirmed=1):
    cursor = conn.cursor()
    try:
        insert_sql = """
            INSERT INTO EMAILCLIENTE (
                id, client_id, email, confirmed, created_at, updated_at
            )
            VALUES (
                EMAILCLIENTE_SEQ.NEXTVAL, :client_id, :email, :confirmed, :created_at, :created_at
            )
        """
        cursor.execute(insert_sql, {
            'client_id': client_id,
            'email': email,
            'confirmed': confirmed,
            'created_at': created_at
        })
    finally:
        cursor.close()

def get_client_by_username(conn, username):
    cursor = conn.cursor()
    try:
        query = "SELECT id, password FROM CLIENTE WHERE username = :username AND active = 1"
        cursor.execute(query, {'username': username})
        return cursor.fetchone()
    finally:
        cursor.close()

def get_client_by_id(conn, client_id):
    cursor = conn.cursor()
    try:
        query = "SELECT id, username, phone, created_at FROM CLIENTE WHERE id = :id AND active = 1"
        cursor.execute(query, {'id': client_id})
        return cursor.fetchone()
    finally:
        cursor.close()

def update_client(conn, client_id, phone=None, email=None):
    cursor = conn.cursor()
    try:
        update_fields = []
        params = {'id': client_id}
        if phone:
            update_fields.append("phone = :phone")
            params["phone"] = phone
        if email:
            update_fields.append("email = :email")
            params["email"] = email
        if update_fields:
            update_sql = "UPDATE CLIENTE SET " + ", ".join(update_fields) + " WHERE id = :id"
            cursor.execute(update_sql, params)
    finally:
        cursor.close()

def delete_client(conn, client_id):
    cursor = conn.cursor()
    try:
        update_sql = "UPDATE CLIENTE SET active = 0 WHERE id = :id"
        cursor.execute(update_sql, {'id': client_id})
    finally:
        cursor.close()

def insert_address(conn, client_id, address, created_at):
    cursor = conn.cursor()
    try:
        insert_sql = """
            INSERT INTO DIRECCION (
                id, client_id, address, created_at, updated_at
            )
            VALUES (
                DIRECCION_SEQ.NEXTVAL, :client_id, :address, :created_at, :created_at
            )
        """
        cursor.execute(insert_sql, {
            'client_id': client_id,
            'address': address,
            'created_at': created_at
        })
    finally:
        cursor.close()

def get_payment_methods_by_client(conn, client_id):
    cursor = conn.cursor()
    try:
        query = """
            SELECT mp.id, mp.name
            FROM MetodoPago mp
            JOIN MetodoPagoCliente mpc ON mp.payment_client_id = mpc.id
            WHERE mpc.client_id = :client_id
        """
        cursor.execute(query, {'client_id': client_id})
        rows = cursor.fetchall()
        payment_methods = []
        for row in rows:
            payment_methods.append({
                "paymentMethodId": row[0],
                "methodName": row[1]
            })
        return payment_methods
    finally:
        cursor.close()

def list_clients_with_payment_methods(conn):
    cursor = conn.cursor()
    try:
        query_clients = """
            SELECT id, name, lastname
            FROM CLIENTE
            WHERE active = 1
        """
        cursor.execute(query_clients)
        clients_rows = cursor.fetchall()
        clients = []
        for row in clients_rows:
            client_id, name, lastname = row
            payment_methods = get_payment_methods_by_client(conn, client_id)
            clients.append({
                "clientId": client_id,
                "name": name,
                "lastname": lastname,
                "paymentMethods": payment_methods
            })
        return clients
    finally:
        cursor.close()
