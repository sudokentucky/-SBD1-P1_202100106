from datetime import datetime
from utils.db import get_connection
from .db_products import *

def get_all_products():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        products = []
        product_rows = get_all_active_products(cursor)
        for row in product_rows:
            product_id, name, price, category = row
            inventory_rows = get_inventory_by_product(cursor, product_id)
            inventory = [
                {"location": inv[0], "stock": int(inv[1])}
                for inv in inventory_rows
            ]
            products.append({
                "id": product_id,
                "name": name,
                "price": float(price),
                "category": category,
                "inventory": inventory
            })
        return {"products": products}, 200
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500
    finally:
        cursor.close()
        conn.close()

def get_product(product_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        row = get_product_details(cursor, product_id)
        if not row:
            return {"status": "error", "message": "Product not found"}, 404
        product = {
            "id": row[0],
            "name": row[1],
            "description": row[2],
            "price": float(row[3]),
            "stock": int(row[4]),
            "category": row[5]
        }
        return product, 200
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500
    finally:
        cursor.close()
        conn.close()

def create_product(data):
    required = ['name', 'price', 'stock', 'category', 'location']
    if not all(data.get(field) for field in required):
        return {"status": "error", "message": "Missing required fields"}, 400

    conn = get_connection()
    cursor = conn.cursor()
    try:
        category_row = get_category_id(cursor, data['category'])
        if not category_row:
            return {"status": "error", "message": "Category not found"}, 404
        category_id = category_row[0]

        location_row = get_location_id(cursor, data['location'])
        if not location_row:
            return {"status": "error", "message": "Location not found"}, 404
        location_id = location_row[0]

        created_at = datetime.now()
        sku = f"{data['name'][:3].upper()}{str(int(created_at.timestamp()))[-5:]}"
        slug = data['name'].lower().replace(' ', '-')

        product_id = insert_product(
            cursor,
            sku,
            data['name'],
            data.get('description'),
            data['price'],
            slug,
            category_id,
            created_at
        )

        insert_inventory(
            cursor,
            product_id,
            location_id,
            data['stock'],
            created_at
        )

        conn.commit()
        return {"status": "success", "message": "Product created", "productId": product_id}, 201
    except Exception as e:
        conn.rollback()
        return {"status": "error", "message": str(e)}, 500
    finally:
        cursor.close()
        conn.close()

def update_product(product_id, data):
    price = data.get('price')
    stock = data.get('stock')
    location = data.get('location')

    if price is None and (stock is None or not location):
        return {"status": "error", "message": "Missing fields to update"}, 400

    conn = get_connection()
    cursor = conn.cursor()
    try:
        updated_at = datetime.now()
        if price is not None:
            update_product_price(cursor, product_id, price, updated_at)

        if stock is not None:
            if not location:
                return {"status": "error", "message": "Location required"}, 400

            location_row = get_location_id(cursor, location)
            if not location_row:
                return {"status": "error", "message": "Location not found"}, 404
            location_id = location_row[0]

            entry = get_inventory_entry(cursor, product_id, location_id)
            if entry:
                update_inventory(cursor, product_id, location_id, stock, updated_at)
            else:
                insert_inventory_entry(cursor, product_id, location_id, stock, updated_at)

        conn.commit()
        return {"status": "success", "message": "Product updated"}, 200
    except Exception as e:
        conn.rollback()
        return {"status": "error", "message": str(e)}, 500
    finally:
        cursor.close()
        conn.close()

def delete_product(product_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        updated_at = datetime.now()
        deactivate_product(cursor, product_id, updated_at)
        conn.commit()
        return {"status": "success", "message": "Product deleted"}, 200
    except Exception as e:
        conn.rollback()
        return {"status": "error", "message": str(e)}, 500
    finally:
        cursor.close()
        conn.close()