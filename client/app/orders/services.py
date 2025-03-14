import datetime
from flask import jsonify
from utils.db import get_connection

from .db_operations import (
    validate_user, validate_payment_method, create_order_record,
    process_order_items, create_payment, create_shipping, get_orders_from_db,
    get_order_by_id
)

def process_order_creation(data):
    if isinstance(data, list):
        conn = get_connection()
        cursor = conn.cursor()
        orders_created = []
        try:
            for order in data:
                user_id = order.get('userId')
                items = order.get('items')
                shipping_address = order.get('shippingAddress')
                payment_method_id = order.get('paymentMethodId')
                
                if not all([user_id, items, shipping_address, payment_method_id]):
                    raise ValueError("Missing required fields in one order")
                if not isinstance(items, list) or len(items) == 0:
                    raise ValueError("Items list is required in each order")
                
                if not validate_user(cursor, user_id):
                    raise ValueError(f"User {user_id} not found")
                if not validate_payment_method(cursor, payment_method_id, user_id):
                    raise ValueError("Invalid payment method")
                
                first_product_id = items[0]['productId']
                cursor.execute("""
                    SELECT s.id FROM INVENTARIO i
                    JOIN SEDE s ON s.id = i.location_id
                    WHERE i.product_id = :product_id ORDER BY i.quantity DESC FETCH FIRST 1 ROWS ONLY
                """, {'product_id': first_product_id})
                location_row = cursor.fetchone()
                if not location_row:
                    raise ValueError(f"No inventory for product {first_product_id}")
                location_id = location_row[0]
                
                order_id = create_order_record(cursor, user_id, location_id)
                total_amount = process_order_items(cursor, order_id, items)
                create_payment(cursor, order_id, payment_method_id, total_amount)
                create_shipping(cursor, order_id, shipping_address)
                
                orders_created.append({
                    "orderId": order_id,
                    "totalAmount": total_amount,
                    "userId": user_id
                })
            conn.commit()
            return jsonify({
                "status": "success",
                "message": "Orders created successfully",
                "orders": orders_created
            }), 201
        except Exception as e:
            conn.rollback()
            return jsonify({"status": "error", "message": str(e)}), 500
        finally:
            cursor.close()
            conn.close()
    else:
        user_id = data.get('userId')
        items = data.get('items')
        shipping_address = data.get('shippingAddress')
        payment_method_id = data.get('paymentMethodId')

        if not all([user_id, items, shipping_address, payment_method_id]):
            return jsonify({"status": "error", "message": "Missing required fields"}), 400
        if not isinstance(items, list) or len(items) == 0:
            return jsonify({"status": "error", "message": "Items list is required"}), 400

        conn = get_connection()
        cursor = conn.cursor()
        try:
            if not validate_user(cursor, user_id):
                return jsonify({"status": "error", "message": f"User {user_id} not found"}), 404
            if not validate_payment_method(cursor, payment_method_id, user_id):
                return jsonify({"status": "error", "message": "Invalid payment method"}), 404

            first_product_id = items[0]['productId']
            cursor.execute("""
                SELECT s.id FROM INVENTARIO i
                JOIN SEDE s ON s.id = i.location_id
                WHERE i.product_id = :product_id ORDER BY i.quantity DESC FETCH FIRST 1 ROWS ONLY
            """, {'product_id': first_product_id})
            location_row = cursor.fetchone()
            if not location_row:
                return jsonify({"status": "error", "message": f"No inventory for product {first_product_id}"}), 404
            location_id = location_row[0]

            order_id = create_order_record(cursor, user_id, location_id)
            total_amount = process_order_items(cursor, order_id, items)
            create_payment(cursor, order_id, payment_method_id, total_amount)
            create_shipping(cursor, order_id, shipping_address)

            conn.commit()

            return jsonify({
                "status": "success",
                "message": "Order created successfully",
                "orderId": order_id,
                "totalAmount": total_amount
            }), 201

        except Exception as e:
            conn.rollback()
            return jsonify({"status": "error", "message": str(e)}), 500

        finally:
            cursor.close()
            conn.close()

def get_orders_list():
    try:
        orders = get_orders_from_db()
        return jsonify({"orders": orders}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

def get_order_details(order_id):
    try:
        order_data = get_order_by_id(order_id)
        if not order_data:
            return jsonify({"status": "error", "message": f"Order {order_id} not found"}), 404
        return jsonify(order_data), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
