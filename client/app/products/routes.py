from flask import Blueprint, request, jsonify
from .products import get_all_products, get_product, create_product, update_product, delete_product

products_bp = Blueprint('products', __name__, url_prefix='/api/products')

@products_bp.route('', methods=['GET'])
def list_products():
    response, status_code = get_all_products()
    return jsonify(response), status_code

@products_bp.route('/<int:id>', methods=['GET'])
def get_product_route(id):
    response, status_code = get_product(id)
    return jsonify(response), status_code

@products_bp.route('', methods=['POST'])
def create_product_route():
    data = request.get_json()
    response, status_code = create_product(data)
    return jsonify(response), status_code

@products_bp.route('/<int:id>', methods=['PUT'])
def update_product_route(id):
    data = request.get_json()
    response, status_code = update_product(id, data)
    return jsonify(response), status_code

@products_bp.route('/<int:id>', methods=['DELETE'])
def delete_product_route(id):
    response, status_code = delete_product(id)
    return jsonify(response), status_code