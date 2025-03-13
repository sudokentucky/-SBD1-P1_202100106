from flask import Blueprint, request, jsonify
from .services import process_order_creation, get_orders_list, get_order_details

orders_bp = Blueprint('orders', __name__, url_prefix='/api/orders')

@orders_bp.route('', methods=['POST'])
def create_order():
    data = request.get_json()
    return process_order_creation(data)

@orders_bp.route('', methods=['GET'])
def list_orders():
    return get_orders_list()

@orders_bp.route('/<int:order_id>', methods=['GET'])
def get_order_detail(order_id):
    return get_order_details(order_id)
