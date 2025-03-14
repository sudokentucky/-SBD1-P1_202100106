
from flask import jsonify
from utils.db import get_connection
from .db_payments import *

def register_payment_service(data):
    if isinstance(data, list):
        conn = get_connection()
        cursor = conn.cursor()
        payments_info = []
        try:
            for payment_data in data:
                payment_result = _process_single_payment(cursor, payment_data)
                if payment_result[1] != 201:
                    raise ValueError(payment_result[0].get("message", "Error in payment"))
                payments_info.append(payment_result[0])
            
            conn.commit()
            return jsonify({
                "status": "success",
                "message": "All payments registered successfully",
                "payments": payments_info
            }), 201
        except Exception as e:
            conn.rollback()
            return jsonify({"status": "error", "message": str(e)}), 500
        finally:
            cursor.close()
            conn.close()
    else:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            response, status_code = _process_single_payment(cursor, data)
            if status_code == 201:
                conn.commit()
            else:
                conn.rollback()
            return jsonify(response), status_code
        except Exception as e:
            conn.rollback()
            return jsonify({"status": "error", "message": str(e)}), 500
        finally:
            cursor.close()
            conn.close()


def _process_single_payment(cursor, data):
    order_id = data.get('orderId')
    amount = data.get('amount')
    payment_method_id = data.get('paymentMethodId')

    if not all([order_id, amount, payment_method_id]):
        return ({
            "status": "error",
            "message": "Missing required fields (orderId, amount, paymentMethodId)"
        }, 400)

    if amount <= 0:
        return ({
            "status": "error",
            "message": "Payment amount must be greater than zero"
        }, 400)

    if not get_order_by_id(cursor, order_id):
        return ({
            "status": "error",
            "message": f"Order {order_id} not found"
        }, 404)

    if not get_payment_method_by_id(cursor, payment_method_id):
        return ({
            "status": "error",
            "message": f"Payment method {payment_method_id} not found"
        }, 404)

    order_status = get_status_of_payment(cursor, order_id)
    subtotal_amount = get_total_order_amount(cursor, order_id)
    
    if order_status == 2 :#orden ya pagada
        return ({
            "status": "error",
            "message": f"The order {order_id} already has a payment registered."
        }, 400)
    
    if amount != subtotal_amount:
        return ({
            "status": "error",
            "message": f"Payment must be exactly {subtotal_amount:.2f} (order total amount)"
        }, 400)
    
    estado_pago_id = 2
    
    payment_id = insert_payment(cursor, order_id, payment_method_id, estado_pago_id, amount)
    
    envio = get_envio_by_order_id(cursor, order_id)
    if envio:
        update_envio(cursor, envio_id=envio[0], order_id=order_id)
    else:
        insert_envio(cursor, order_id=order_id)

    return ({
        "status": "success",
        "message": "Payment registered successfully",
        "paymentId": payment_id,
        "paymentStatus": "PAID",
        "totalPaid": amount,
        "remainingAmount": 0
    }, 201)

def list_payments_service(filters):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        rows = list_payments(cursor, filters)

        payments = []
        for row in rows:
            payments.append({
                "paymentId": row[0],
                "orderId": row[1],
                "amount": float(row[2]),
                "method": row[3],
                "status": row[4],
                "createdAt": row[5].strftime('%Y-%m-%dT%H:%M:%SZ') if row[5] else None
            })

        return jsonify({
            "payments": payments
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

    finally:
        cursor.close()
        conn.close()