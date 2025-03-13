from flask import jsonify
from utils.db import get_connection
from .db_payments import (
    get_order_by_id,
    get_payment_method_by_id,
    get_total_order_amount,
    get_total_paid_amount,
    insert_payment,
    get_envio_by_order_id,
    update_envio,
    insert_envio,
    list_payments as db_list_payments
)

def register_payment_service(data):
    order_id = data.get('orderId')
    amount = data.get('amount')
    payment_method_id = data.get('paymentMethodId')

    if not all([order_id, amount, payment_method_id]):
        return jsonify({
            "status": "error",
            "message": "Missing required fields (orderId, amount, paymentMethodId)"
        }), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()

        if not get_order_by_id(cursor, order_id):
            return jsonify({
                "status": "error",
                "message": f"Order {order_id} not found"
            }), 404

        if not get_payment_method_by_id(cursor, payment_method_id):
            return jsonify({
                "status": "error",
                "message": f"Payment method {payment_method_id} not found"
            }), 404

        total_order_amount = get_total_order_amount(cursor, order_id)
        total_paid_so_far = get_total_paid_amount(cursor, order_id)

        if total_paid_so_far >= total_order_amount:
            return jsonify({
                "status": "error",
                "message": f"The order {order_id} is already fully paid and cannot receive more payments."
            }), 400

        remaining_amount = total_order_amount - total_paid_so_far

        if amount > remaining_amount:
            return jsonify({
                "status": "error",
                "message": f"Payment exceeds the remaining amount. Remaining: {remaining_amount:.2f}"
            }), 400

        new_total_paid = total_paid_so_far + amount
        estado_pago_id = 1 if new_total_paid >= total_order_amount else 0  # 1 = PAID, 0 = PENDING

        payment_id = insert_payment(cursor, order_id, payment_method_id, estado_pago_id, amount)

        if estado_pago_id == 1:
            envio = get_envio_by_order_id(cursor, order_id)
            if envio:
                update_envio(cursor, envio_id=envio[0], order_id=order_id)
            else:
                insert_envio(cursor, order_id=order_id)

        conn.commit()

        return jsonify({
            "status": "success",
            "message": "Payment registered successfully",
            "paymentId": payment_id,
            "paymentStatus": "approved" if estado_pago_id == 1 else "pending",
            "totalPaid": new_total_paid,
            "remainingAmount": round(total_order_amount - new_total_paid, 2)
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

def list_payments_service(filters):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        rows = db_list_payments(cursor, filters)

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