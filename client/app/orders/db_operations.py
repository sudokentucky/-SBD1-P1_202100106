from utils.db import get_connection

def validate_user(cursor, user_id):
    cursor.execute("SELECT id FROM CLIENTE WHERE id = :id AND active = 1", {'id': user_id})
    return cursor.fetchone()

def validate_payment_method(cursor, payment_method_id, user_id):
    cursor.execute("""
        SELECT mp.id FROM MetodoPago mp
        JOIN MetodoPagoCliente mpc ON mpc.id = mp.payment_client_id
        WHERE mp.id = :payment_method_id AND mpc.client_id = :user_id
    """, {'payment_method_id': payment_method_id, 'user_id': user_id})
    return cursor.fetchone()

def create_order_record(cursor, user_id, location_id):
    cursor.execute("""
        INSERT INTO OrdenCompra (id, client_id, location_id, created_at, updated_at)
        VALUES (ORDENCOMPRA_SEQ.NEXTVAL, :client_id, :location_id, SYSDATE, SYSDATE)
    """, {'client_id': user_id, 'location_id': location_id})
    cursor.execute("SELECT ORDENCOMPRA_SEQ.CURRVAL FROM dual")
    return cursor.fetchone()[0]

def process_order_items(cursor, order_id, items):
    total_amount = 0.0

    for item in items:
        product_id = item.get('productId')
        quantity = item.get('quantity')

        if product_id is None or quantity is None:
            raise Exception("Each item must include productId and quantity")

        if not isinstance(quantity, int) or quantity <= 0:
            raise Exception(f"Invalid quantity '{quantity}' for product {product_id}. Must be a positive integer.")

        cursor.execute("""
            SELECT price FROM PRODUCTO 
            WHERE id = :product_id AND active = 1
        """, {'product_id': product_id})

        price_row = cursor.fetchone()

        if not price_row:
            raise Exception(f"Product {product_id} not found or inactive")

        unit_price = float(price_row[0])
        subtotal = unit_price * quantity
        total_amount += subtotal
        cursor.execute("""
            INSERT INTO DetalleOrden (
                id, order_id, product_id, quantity, unit_price, subtotal, created_at, updated_at
            )
            VALUES (
                DETALLEORDEN_SEQ.NEXTVAL, :order_id, :product_id, :quantity, :unit_price, :subtotal, SYSDATE, SYSDATE
            )
        """, {
            'order_id': order_id,
            'product_id': product_id,
            'quantity': quantity,
            'unit_price': unit_price,
            'subtotal': subtotal
        })

    return total_amount


def create_payment(cursor, order_id, payment_method_id, total_amount):
    cursor.execute("""
        INSERT INTO Pago (id, order_id, metodo_pago_id, estado_pago_id, total_amount, created_at, updated_at)
        VALUES (PAGO_SEQ.NEXTVAL, :order_id, :payment_method_id, 1, :total_amount, SYSDATE, SYSDATE)
    """, {
        'order_id': order_id,
        'payment_method_id': payment_method_id,
        'total_amount': total_amount
    })

def create_shipping(cursor, order_id, shipping_address):
    cursor.execute("""
        INSERT INTO Envio (id, order_id, company_id, shipping_status_id, address, number_company_guide, dispatch_date, created_at, updated_at)
        VALUES (ENVIO_SEQ.NEXTVAL, :order_id, 1, 1, :address, 'G'||:order_id, SYSDATE, SYSDATE, SYSDATE)
    """, {'order_id': order_id, 'address': shipping_address})

def get_orders_from_db():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT
                o.id AS order_id,
                o.client_id,
                NVL(SUM(d.subtotal), 0) AS total_amount,
                o.created_at
            FROM ORDENCOMPRA o
            LEFT JOIN DETALLEORDEN d ON d.order_id = o.id
            GROUP BY o.id, o.client_id, o.created_at
            ORDER BY o.created_at DESC
        """)

        rows = cursor.fetchall()
        orders = []

        for row in rows:
            orders.append({
                "orderId": row[0],
                "userId": row[1],
                "totalAmount": float(row[2]),
                "createdAt": row[3].strftime('%Y-%m-%d') if row[3] else None
            })

        return orders

    finally:
        cursor.close()
        conn.close()

def get_order_by_id(order_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT
                o.id,
                o.client_id,
                NVL(SUM(d.subtotal), 0) AS total_amount,
                o.created_at
            FROM ORDENCOMPRA o
            LEFT JOIN DETALLEORDEN d ON d.order_id = o.id
            WHERE o.id = :order_id
            GROUP BY o.id, o.client_id, o.created_at
        """, {'order_id': order_id})

        order_row = cursor.fetchone()

        if not order_row:
            return None

        cursor.execute("""
            SELECT
                product_id,
                quantity,
                unit_price,
                subtotal
            FROM DETALLEORDEN
            WHERE order_id = :order_id
        """, {'order_id': order_id})

        item_rows = cursor.fetchall()
        items = []

        for item in item_rows:
            items.append({
                "productId": item[0],
                "quantity": item[1],
                "price": float(item[2]),
                "subtotal": float(item[3])
            })

        return {
            "orderId": order_row[0],
            "userId": order_row[1],
            "items": items,
            "totalAmount": float(order_row[2]),
            "createdAt": order_row[3].strftime('%Y-%m-%d') if order_row[3] else None
        }

    finally:
        cursor.close()
        conn.close()
