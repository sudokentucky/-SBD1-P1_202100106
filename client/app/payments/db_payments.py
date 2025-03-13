import random
import datetime

def get_order_by_id(cursor, order_id):
    cursor.execute("""
        SELECT id
        FROM OrdenCompra
        WHERE id = :order_id
    """, {'order_id': order_id})
    return cursor.fetchone()

def get_payment_method_by_id(cursor, payment_method_id):
    cursor.execute("""
        SELECT id
        FROM MetodoPago
        WHERE id = :payment_method_id
    """, {'payment_method_id': payment_method_id})
    return cursor.fetchone()

def get_total_order_amount(cursor, order_id):
    cursor.execute("""
        SELECT NVL(SUM(subtotal), 0)
        FROM DetalleOrden
        WHERE order_id = :order_id
    """, {'order_id': order_id})
    return float(cursor.fetchone()[0])

def get_total_paid_amount(cursor, order_id):
    cursor.execute("""
        SELECT NVL(SUM(total_amount), 0)
        FROM Pago
        WHERE order_id = :order_id
    """, {'order_id': order_id})
    return float(cursor.fetchone()[0])

def insert_payment(cursor, order_id, payment_method_id, estado_pago_id, amount):
    created_at = datetime.datetime.now()

    cursor.execute("""
        INSERT INTO Pago (
            id, order_id, metodo_pago_id, estado_pago_id,
            total_amount, created_at, updated_at
        )
        VALUES (
            PAGO_SEQ.NEXTVAL, :order_id, :payment_method_id, :estado_pago_id,
            :total_amount, :created_at, :created_at
        )
    """, {
        'order_id': order_id,
        'payment_method_id': payment_method_id,
        'estado_pago_id': estado_pago_id,
        'total_amount': amount,
        'created_at': created_at
    })

    cursor.execute("SELECT PAGO_SEQ.CURRVAL FROM dual")
    return cursor.fetchone()[0]

def get_envio_by_order_id(cursor, order_id):
    cursor.execute("""
        SELECT id
        FROM Envio
        WHERE order_id = :order_id
    """, {'order_id': order_id})
    return cursor.fetchone()

def update_envio(cursor, envio_id, order_id):
    created_at = datetime.datetime.now()
    company_id = random.randint(1, 3)
    shipping_status_id = 1
    guide_number = f"G{order_id:04d}"

    cursor.execute("""
        UPDATE Envio
        SET company_id = :company_id,
            shipping_status_id = :shipping_status_id,
            number_company_guide = :guide_number,
            dispatch_date = :dispatch_date,
            delivered_at = :delivered_at,
            updated_at = :updated_at
        WHERE id = :envio_id
    """, {
        'company_id': company_id,
        'shipping_status_id': shipping_status_id,
        'guide_number': guide_number,
        'dispatch_date': created_at,
        'delivered_at': created_at,
        'updated_at': created_at,
        'envio_id': envio_id
    })

def insert_envio(cursor, order_id):
    created_at = datetime.datetime.now()
    company_id = random.randint(1, 3)
    shipping_status_id = 1
    guide_number = f"G{order_id:04d}"

    cursor.execute("""
        INSERT INTO Envio (
            id, order_id, company_id, shipping_status_id, address,
            number_company_guide, dispatch_date, delivered_at,
            created_at, updated_at
        )
        VALUES (
            ENVIO_SEQ.NEXTVAL, :order_id, :company_id, :shipping_status_id, 
            'Dirección pendiente', :guide_number, :dispatch_date, :delivered_at,
            :created_at, :created_at
        )
    """, {
        'order_id': order_id,
        'company_id': company_id,
        'shipping_status_id': shipping_status_id,
        'guide_number': guide_number,
        'dispatch_date': created_at,
        'delivered_at': created_at,
        'created_at': created_at
    })

def list_payments(cursor, filters):
    query = """
        SELECT 
            p.id AS payment_id,
            p.order_id,
            p.total_amount,
            mp.name AS payment_method,
            ep.name AS payment_status,
            p.created_at
        FROM Pago p
        JOIN MetodoPago mp ON mp.id = p.metodo_pago_id
        JOIN EstadoPago ep ON ep.id = p.estado_pago_id
        WHERE 1 = 1
    """

    params = {}

    if filters.get('orderId'):
        query += " AND p.order_id = :order_id"
        params['order_id'] = filters['orderId']

    if filters.get('paymentMethodId'):
        query += " AND p.metodo_pago_id = :payment_method_id"
        params['payment_method_id'] = filters['paymentMethodId']

    if filters.get('dateFrom'):
        query += " AND p.created_at >= TO_DATE(:date_from, 'YYYY-MM-DD')"
        params['date_from'] = filters['dateFrom']

    if filters.get('dateTo'):
        query += " AND p.created_at <= TO_DATE(:date_to, 'YYYY-MM-DD')"
        params['date_to'] = filters['dateTo']

    query += " ORDER BY p.created_at DESC"

    cursor.execute(query, params)
    return cursor.fetchall()
