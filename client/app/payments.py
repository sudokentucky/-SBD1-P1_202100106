from flask import Blueprint, request, jsonify
import datetime
import random
from utils.db import get_connection

payments_bp = Blueprint('payments', __name__, url_prefix='/api/payments')

@payments_bp.route('', methods=['POST'])
def register_payment():
    data = request.get_json()

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
        cursor.execute("""
            SELECT id FROM OrdenCompra WHERE id = :order_id
        """, {'order_id': order_id})
        order_row = cursor.fetchone()

        if not order_row:
            return jsonify({
                "status": "error",
                "message": f"Order {order_id} not found"
            }), 404

        cursor.execute("""
            SELECT id FROM MetodoPago WHERE id = :payment_method_id
        """, {'payment_method_id': payment_method_id})
        payment_method_row = cursor.fetchone()

        if not payment_method_row:
            return jsonify({
                "status": "error",
                "message": f"Payment method {payment_method_id} not found"
            }), 404

        cursor.execute("""
            SELECT NVL(SUM(subtotal), 0)
            FROM DetalleOrden
            WHERE order_id = :order_id
        """, {'order_id': order_id})

        total_order_amount = float(cursor.fetchone()[0])
        cursor.execute("""
            SELECT NVL(SUM(total_amount), 0)
            FROM Pago
            WHERE order_id = :order_id
        """, {'order_id': order_id})

        total_paid_so_far = float(cursor.fetchone()[0])
        new_total_paid = total_paid_so_far + float(amount)
        if new_total_paid >= total_order_amount:
            estado_pago_id = 1  
        else:
            estado_pago_id = 0 

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
        payment_id = cursor.fetchone()[0]

        if estado_pago_id == 1:
            cursor.execute("""
                SELECT id FROM Envio WHERE order_id = :order_id
            """, {'order_id': order_id})
            envio_row = cursor.fetchone()

            company_id = random.randint(1, 5)  
            shipping_status_id = 2  
            guide_number = f"G{order_id:04d}"
            dispatch_date = created_at
            delivered_at = created_at

            if envio_row:
                envio_id = envio_row[0]
                # Actualizar envío existente
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
                    'dispatch_date': dispatch_date,
                    'delivered_at': delivered_at,
                    'updated_at': created_at,
                    'envio_id': envio_id
                })

            else:
                cursor.execute("""
                    INSERT INTO Envio (
                        id, order_id, company_id, shipping_status_id, address,
                        number_company_guide, dispatch_date, delivered_at,
                        created_at, updated_at
                    )
                    SELECT
                        ENVIO_SEQ.NEXTVAL, :order_id, :company_id, :shipping_status_id, 
                        'Dirección pendiente', :guide_number, :dispatch_date, :delivered_at,
                        :created_at, :created_at
                    FROM dual
                """, {
                    'order_id': order_id,
                    'company_id': company_id,
                    'shipping_status_id': shipping_status_id,
                    'guide_number': guide_number,
                    'dispatch_date': dispatch_date,
                    'delivered_at': delivered_at,
                    'created_at': created_at
                })

        conn.commit()

        return jsonify({
            "status": "success",
            "message": "Payment registered successfully",
            "paymentId": payment_id,
            "paymentStatus": "approved" if estado_pago_id == 1 else "pending",
            "totalPaid": new_total_paid,
            "remainingAmount": max(total_order_amount - new_total_paid, 0)
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
