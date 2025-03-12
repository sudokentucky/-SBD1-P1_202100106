from flask import Blueprint, request, jsonify
import datetime
from utils.db import get_connection

products_bp = Blueprint('products', __name__, url_prefix='/api/products')

@products_bp.route('', methods=['GET'])
def list_products():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        query_products = """
            SELECT p.id, p.name, p.price, c.name AS category
            FROM PRODUCTO p
            JOIN CATEGORIA c ON p.category_id = c.id
            WHERE p.active = 1
        """
        cursor.execute(query_products)
        product_rows = cursor.fetchall()

        products = []

        for row in product_rows:
            product_id = row[0]
            name = row[1]
            price = float(row[2])
            category = row[3]

            query_inventory = """
                SELECT s.name AS location, i.quantity AS stock
                FROM INVENTARIO i
                JOIN SEDE s ON i.location_id = s.id
                WHERE i.product_id = :product_id
            """
            cursor.execute(query_inventory, {'product_id': product_id})
            inventory_rows = cursor.fetchall()

            inventory_list = []
            for inv in inventory_rows:
                inventory_list.append({
                    "location": inv[0],
                    "stock": int(inv[1])
                })

            product_data = {
                "id": product_id,
                "name": name,
                "price": price,
                "category": category,
                "inventory": inventory_list
            }

            products.append(product_data)

        return jsonify({"products": products}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

    finally:
        cursor.close()
        conn.close()

