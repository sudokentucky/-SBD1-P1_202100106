from flask import Blueprint, request, jsonify
from .payments import register_payment_service, list_payments_service

payments_bp = Blueprint('payments', __name__, url_prefix='/api/payments')

@payments_bp.route('', methods=['POST'])
def register_payment():
    data = request.get_json()
    return register_payment_service(data)

@payments_bp.route('', methods=['GET'])
def list_payments():
    filters = {
        "orderId": request.args.get('orderId', type=int),
        "dateFrom": request.args.get('dateFrom'),
        "dateTo": request.args.get('dateTo'),
        "paymentMethodId": request.args.get('paymentMethodId', type=int)
    }
    return list_payments_service(filters)
