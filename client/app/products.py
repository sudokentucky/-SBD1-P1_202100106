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


@products_bp.route('/<int:id>', methods=['GET'])
def get_product(id):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT p.id, p.name, p.description, p.price,
            NVL(SUM(i.quantity), 0) AS stock,
            c.name AS category
        FROM PRODUCTO p
        LEFT JOIN INVENTARIO i ON p.id = i.product_id
        JOIN CATEGORIA c ON p.category_id = c.id
        WHERE p.id = :id AND p.active = 1
        GROUP BY p.id, p.name, p.description, p.price, c.name
    """
    cursor.execute(query, {'id': id})
    row = cursor.fetchone()

    if not row:
        cursor.close()
        conn.close()
        return jsonify({"status": "error", "message": "Product not found"}), 404

    product = {
        "id": row[0],
        "name": row[1],
        "description": row[2],
        "price": float(row[3]),
        "stock": int(row[4]),
        "category": row[5]
    }

    cursor.close()
    conn.close()
    return jsonify(product), 200

@products_bp.route('', methods=['POST'])
def create_product():
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')
    price = data.get('price')
    stock = data.get('stock')
    category_name = data.get('category')
    location_name = data.get('location')

    # Validación básica
    if not all([name, price, stock, category_name, location_name]):
        return jsonify({
            "status": "error",
            "message": "Missing required fields"
        }), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id FROM CATEGORIA WHERE name = :category
        """, {'category': category_name})
        category_row = cursor.fetchone()

        if not category_row:
            return jsonify({
                "status": "error",
                "message": f"Category '{category_name}' not found"
            }), 404

        category_id = category_row[0]

        cursor.execute("""
            SELECT id FROM SEDE WHERE name = :location
        """, {'location': location_name})
        location_row = cursor.fetchone()

        if not location_row:
            return jsonify({
                "status": "error",
                "message": f"Location '{location_name}' not found"
            }), 404

        location_id = location_row[0]

        created_at = datetime.datetime.now()
        sku = f"{name[:3].upper()}{str(int(datetime.datetime.timestamp(created_at)))[-5:]}"  
        slug = name.lower().replace(' ', '-')

        cursor.execute("""
            INSERT INTO PRODUCTO (
                id, sku, name, description, price, slug, active, category_id, created_at, updated_at
            )
            VALUES (
                PRODUCTO_SEQ.NEXTVAL, :sku, :name, :description, :price, :slug, :active, :category_id, :created_at, :created_at
            )
        """, {
            'sku': sku,
            'name': name,
            'description': description,
            'price': price,
            'slug': slug,
            'active': '1',
            'category_id': category_id,
            'created_at': created_at
        })

        cursor.execute("SELECT PRODUCTO_SEQ.CURRVAL FROM dual")
        product_id = cursor.fetchone()[0]
        cursor.execute("""
            INSERT INTO INVENTARIO (
                id, quantity, product_id, location_id, created_at, updated_at
            )
            VALUES (
                INVENTARIO_SEQ.NEXTVAL, :quantity, :product_id, :location_id, :created_at, :created_at
            )
        """, {
            'quantity': stock,
            'product_id': product_id,
            'location_id': location_id,
            'created_at': created_at
        })

        conn.commit()

        return jsonify({
            "status": "success",
            "message": "Product created successfully",
            "productId": product_id
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


@products_bp.route('/<int:id>', methods=['PUT'])
def update_product(id):
    data = request.get_json()

    price = data.get('price')
    stock = data.get('stock')
    location = data.get('location')
    if price is None and (stock is None or not location):
        return jsonify({
            "status": "error",
            "message": "Missing fields to update: provide price and/or stock with location"
        }), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()

        updated_at = datetime.datetime.now()
        if price is not None:
            cursor.execute("""
                UPDATE PRODUCTO
                SET price = :price, updated_at = :updated_at
                WHERE id = :id
            """, {
                'price': price,
                'updated_at': updated_at,
                'id': id
            })

        if stock is not None:
            if not location:
                return jsonify({
                    "status": "error",
                    "message": "Missing location for inventory update"
                }), 400
            cursor.execute("""
                SELECT id FROM SEDE WHERE name = :location
            """, {'location': location})
            sede_row = cursor.fetchone()

            if not sede_row:
                return jsonify({
                    "status": "error",
                    "message": f"Location '{location}' not found"
                }), 404

            location_id = sede_row[0]
            cursor.execute("""
                SELECT id FROM INVENTARIO
                WHERE product_id = :product_id AND location_id = :location_id
            """, {
                'product_id': id,
                'location_id': location_id
            })
            inventory_row = cursor.fetchone()

            if inventory_row:
                cursor.execute("""
                    UPDATE INVENTARIO
                    SET quantity = :stock, updated_at = :updated_at
                    WHERE product_id = :product_id AND location_id = :location_id
                """, {
                    'stock': stock,
                    'updated_at': updated_at,
                    'product_id': id,
                    'location_id': location_id
                })
            else:
                cursor.execute("""
                    INSERT INTO INVENTARIO (id, quantity, product_id, location_id, created_at, updated_at)
                    VALUES (INVENTARIO_SEQ.NEXTVAL, :quantity, :product_id, :location_id, :created_at, :updated_at)
                """, {
                    'quantity': stock,
                    'product_id': id,
                    'location_id': location_id,
                    'created_at': updated_at,
                    'updated_at': updated_at
                })

        conn.commit()

        return jsonify({
            "status": "success",
            "message": "Product and/or inventory updated successfully"
        }), 200

    except Exception as e:
        conn.rollback()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

    finally:
        cursor.close()
        conn.close()

@products_bp.route('/<int:id>', methods=['DELETE'])
def delete_product(id):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE PRODUCTO SET active = 0, updated_at = :updated_at
            WHERE id = :id
        """, {
            'updated_at': datetime.datetime.now(),
            'id': id
        })

        conn.commit()

        return jsonify({
            "status": "success",
            "message": "Product deleted successfully"
        }), 200

    except Exception as e:
        conn.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

    finally:
        cursor.close()
        conn.close()