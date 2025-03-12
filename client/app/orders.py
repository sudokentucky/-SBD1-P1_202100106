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
        cursor.execute("""
            SELECT id FROM CLIENTE WHERE id = :id AND active = 1
        """, {'id': user_id})
        cliente_row = cursor.fetchone()

        if not cliente_row:
            return jsonify({
                "status": "error",
                "message": f"User {user_id} not found or inactive"
            }), 404
        cursor.execute("""
            SELECT mp.id
            FROM MetodoPago mp
            JOIN MetodoPagoCliente mpc ON mpc.id = mp.payment_client_id
            WHERE mp.id = :payment_method_id AND mpc.client_id = :user_id
        """, {
            'payment_method_id': payment_method_id,
            'user_id': user_id
        })

        payment_method_row = cursor.fetchone()

        if not payment_method_row:
            return jsonify({
                "status": "error",
                "message": f"Payment method {payment_method_id} not found or not associated with user {user_id}"
            }), 404

        created_at = datetime.datetime.now()
        first_product_id = items[0]['productId']
        cursor.execute("""
            SELECT s.id, s.name
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
        order_id = cursor.fetchone()[0]

        total_amount = 0.0
        for item in items:
            product_id = item.get('productId')
            quantity = item.get('quantity')

            if not product_id or quantity is None:
                conn.rollback()
                return jsonify({
                    "status": "error",
                    "message": "Each item must include productId and quantity"
                }), 400
            cursor.execute("""
                SELECT i.id, i.quantity, s.id AS sede_id, s.name
                FROM INVENTARIO i
                JOIN SEDE s ON s.id = i.location_id
                WHERE i.product_id = :product_id AND i.quantity >= :required_quantity
                ORDER BY i.quantity DESC
                FETCH FIRST 1 ROWS ONLY
            """, {
                'product_id': product_id,
                'required_quantity': quantity
            })

            inventario_row = cursor.fetchone()

            if not inventario_row:
                conn.rollback()
                return jsonify({
                    "status": "error",
                    "message": f"Insufficient stock for product {product_id}"
                }), 400

            inventario_id = inventario_row[0]
            current_quantity = inventario_row[1]
            cursor.execute("""
                SELECT price FROM PRODUCTO
                WHERE id = :product_id AND active = 1
            """, {'product_id': product_id})
            product_row = cursor.fetchone()

            if not product_row:
                conn.rollback()
                return jsonify({
                    "status": "error",
                    "message": f"Product {product_id} not found or inactive"
                }), 404

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
