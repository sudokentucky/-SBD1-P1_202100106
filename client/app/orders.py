from flask import Blueprint, request, jsonify
import datetime
from utils.db import get_connection

orders_bp = Blueprint('orders', __name__, url_prefix='/api/orders')

@orders_bp.route('/payment_methods', methods=['POST'])
def create_payment_method():
    data = request.get_json()

    user_id = data.get('userId')
    payment_method_name = data.get('paymentMethod')
    if not user_id or not payment_method_name:
        return jsonify({
            "status": "error",
            "message": "Missing userId or paymentMethod"
        }), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id FROM CLIENTE WHERE id = :id AND active = 1
        """, {'id': user_id})

        cliente_row = cursor.fetchone()

        if not cliente_row:
            return jsonify({
                "status": "error",
                "message": f"User {user_id} not found or inactive"
            }), 404

        created_at = datetime.datetime.now()
        cursor.execute("""
            INSERT INTO MetodoPagoCliente (
                id, client_id, created_at, updated_at
            )
            VALUES (
                METODOPAGOCLIENTE_SEQ.NEXTVAL, :client_id, :created_at, :created_at
            )
        """, {
            'client_id': user_id,
            'created_at': created_at
        })
        cursor.execute("SELECT METODOPAGOCLIENTE_SEQ.CURRVAL FROM dual")
        payment_client_id = cursor.fetchone()[0]
        cursor.execute("""
            INSERT INTO MetodoPago (
                id, payment_client_id, name, created_at, updated_at
            )
            VALUES (
                METODOPAGO_SEQ.NEXTVAL, :payment_client_id, :name, :created_at, :created_at
            )
        """, {
            'payment_client_id': payment_client_id,
            'name': payment_method_name,
            'created_at': created_at
        })

        conn.commit()

        return jsonify({
            "status": "success",
            "message": "Payment method registered successfully",
            "paymentClientId": payment_client_id
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

def validate_user(cursor, user_id):
    cursor.execute("""
        SELECT id FROM CLIENTE WHERE id = :id AND active = 1
    """, {'id': user_id})
    return cursor.fetchone()

def validate_payment_method(cursor, payment_method_id, user_id):
    cursor.execute("""
        SELECT mp.id
        FROM MetodoPago mp
        JOIN MetodoPagoCliente mpc ON mpc.id = mp.payment_client_id
        WHERE mp.id = :payment_method_id AND mpc.client_id = :user_id
    """, {
        'payment_method_id': payment_method_id,
        'user_id': user_id
    })
    return cursor.fetchone()

def create_order(cursor, user_id, location_id):
    created_at = datetime.datetime.now()

    cursor.execute("""
        INSERT INTO OrdenCompra (
            id, client_id, location_id, created_at, updated_at
        )
        VALUES (
            ORDENCOMPRA_SEQ.NEXTVAL, :client_id, :location_id, :created_at, :created_at
        )
    """, {
        'client_id': user_id,
        'location_id': location_id,
        'created_at': created_at
    })

    cursor.execute("SELECT ORDENCOMPRA_SEQ.CURRVAL FROM dual")
    return cursor.fetchone()[0]

def process_order_items(cursor, order_id, items):
    total_amount = 0.0
    created_at = datetime.datetime.now()

    for item in items:
        product_id = item.get('productId')
        quantity = item.get('quantity')

        # Validación básica
        if not product_id or quantity is None:
            raise Exception("Each item must include productId and quantity")

        cursor.execute("""
            SELECT i.id, i.quantity
            FROM INVENTARIO i
            WHERE i.product_id = :product_id AND i.quantity >= :required_quantity
            ORDER BY i.quantity DESC
            FETCH FIRST 1 ROWS ONLY
        """, {
            'product_id': product_id,
            'required_quantity': quantity
        })

        inventario_row = cursor.fetchone()
        if not inventario_row:
            raise Exception(f"Insufficient stock for product {product_id}")

        inventario_id, current_quantity = inventario_row

        cursor.execute("""
            SELECT price FROM PRODUCTO WHERE id = :product_id AND active = 1
        """, {'product_id': product_id})

        product_row = cursor.fetchone()
        if not product_row:
            raise Exception(f"Product {product_id} not found or inactive")

        unit_price = float(product_row[0])
        subtotal = unit_price * quantity
        total_amount += subtotal

        cursor.execute("""
            INSERT INTO DetalleOrden (
                id, order_id, product_id, quantity, unit_price, created_at, updated_at
            )
            VALUES (
                DETALLEORDEN_SEQ.NEXTVAL, :order_id, :product_id, :quantity, :unit_price, :created_at, :created_at
            )
        """, {
            'order_id': order_id,
            'product_id': product_id,
            'quantity': quantity,
            'unit_price': unit_price,
            'created_at': created_at
        })

        new_quantity = current_quantity - quantity
        cursor.execute("""
            UPDATE INVENTARIO
            SET quantity = :new_quantity, updated_at = :updated_at
            WHERE id = :inventario_id
        """, {
            'new_quantity': new_quantity,
            'updated_at': created_at,
            'inventario_id': inventario_id
        })

    return total_amount

def create_payment(cursor, order_id, payment_method_id, total_amount):
    created_at = datetime.datetime.now()
    estado_pago_id = 0 #Inicialmente el estado del pago es 0 (pendiente)

    cursor.execute("""
        INSERT INTO Pago (
            id, order_id, metodo_pago_id, estado_pago_id, total_amount, created_at, updated_at
        )
        VALUES (
            PAGO_SEQ.NEXTVAL, :order_id, :payment_method_id, :estado_pago_id, :total_amount, :created_at, :created_at
        )
    """, {
        'order_id': order_id,
        'payment_method_id': payment_method_id,
        'estado_pago_id': estado_pago_id,
        'total_amount': total_amount,
        'created_at': created_at
    })

def create_shipping(cursor, order_id, shipping_address):
    created_at = datetime.datetime.now()
    company_id = 1
    shipping_status_id = 1
    guide_number = f"G{order_id:04d}"  

    cursor.execute("""
        INSERT INTO Envio (
            id, order_id, company_id, shipping_status_id, address, number_company_guide,
            dispatch_date, created_at, updated_at
        )
        VALUES (
            ENVIO_SEQ.NEXTVAL, :order_id, :company_id, :shipping_status_id, :address, :guide_number,
            :dispatch_date, :created_at, :created_at
        )
    """, {
        'order_id': order_id,
        'company_id': company_id,
        'shipping_status_id': shipping_status_id,
        'address': shipping_address,
        'guide_number': guide_number,
        'dispatch_date': created_at,
        'created_at': created_at
    })

@orders_bp.route('', methods=['POST'])
def create_order():
    data = request.get_json()

    user_id = data.get('userId')
    items = data.get('items')
    shipping_address = data.get('shippingAddress')
    payment_method_id = data.get('paymentMethodId')

    if not all([user_id, items, shipping_address, payment_method_id]):
        return jsonify({
            "status": "error",
            "message": "Missing required fields"
        }), 400

    if not isinstance(items, list) or len(items) == 0:
        return jsonify({
            "status": "error",
            "message": "Items list is required and cannot be empty"
        }), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()

        if not validate_user(cursor, user_id):
            return jsonify({
                "status": "error",
                "message": f"User {user_id} not found or inactive"
            }), 404

        if not validate_payment_method(cursor, payment_method_id, user_id):
            return jsonify({
                "status": "error",
                "message": f"Payment method {payment_method_id} not found or not associated with user {user_id}"
            }), 404

        first_product_id = items[0]['productId']
        cursor.execute("""
            SELECT s.id
            FROM INVENTARIO i
            JOIN SEDE s ON s.id = i.location_id
            WHERE i.product_id = :product_id
            ORDER BY i.quantity DESC
            FETCH FIRST 1 ROWS ONLY
        """, {'product_id': first_product_id})

        location_row = cursor.fetchone()
        if not location_row:
            return jsonify({
                "status": "error",
                "message": f"No inventory found for product {first_product_id}"
            }), 404

        location_id = location_row[0]
        order_id = create_order(cursor, user_id, location_id)
        total_amount = process_order_items(cursor, order_id, items)
        create_payment(cursor, order_id, payment_method_id, total_amount)
        create_shipping(cursor, order_id, shipping_address)
        conn.commit()

        return jsonify({
            "status": "success",
            "message": "Order created successfully",
            "orderId": order_id,
            "totalAmount": total_amount,
            "orderStatus": "processing"
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


@orders_bp.route('', methods=['GET'])
def list_orders():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = """
            SELECT
                o.id AS order_id,
                o.client_id,
                NVL(SUM(d.quantity * d.unit_price), 0) AS total_amount,
                o.created_at
            FROM ORDENCOMPRA o
            LEFT JOIN DETALLEORDEN d ON d.order_id = o.id
            GROUP BY o.id, o.client_id, o.created_at
            ORDER BY o.created_at DESC
        """

        cursor.execute(query)
        rows = cursor.fetchall()

        orders = []
        for row in rows:
            orders.append({
                "orderId": row[0],
                "userId": row[1],
                "totalAmount": float(row[2]),
                "createdAt": row[3].strftime('%Y-%m-%d') if row[3] else None
            })

        return jsonify({
            "orders": orders
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

    finally:
        cursor.close()
        conn.close()

@orders_bp.route('/<int:order_id>', methods=['GET'])
def get_order_detail(order_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                o.id,
                o.client_id,
                NVL(SUM(d.quantity * d.unit_price), 0) AS total_amount,
                o.created_at
            FROM ORDENCOMPRA o
            LEFT JOIN DETALLEORDEN d ON d.order_id = o.id
            WHERE o.id = :order_id
            GROUP BY o.id, o.client_id, o.created_at
        """, {'order_id': order_id})

        order_row = cursor.fetchone()

        if not order_row:
            return jsonify({
                "status": "error",
                "message": f"Order {order_id} not found"
            }), 404
        cursor.execute("""
            SELECT
                product_id,
                quantity,
                unit_price
            FROM DETALLEORDEN
            WHERE order_id = :order_id
        """, {'order_id': order_id})

        item_rows = cursor.fetchall()

        items = []
        for item in item_rows:
            items.append({
                "productId": item[0],
                "quantity": item[1],
                "price": float(item[2])
            })

        return jsonify({
            "orderId": order_row[0],
            "userId": order_row[1],
            "items": items,
            "totalAmount": float(order_row[2]),
            "createdAt": order_row[3].strftime('%Y-%m-%d') if order_row[3] else None
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

    finally:
        cursor.close()
        conn.close()