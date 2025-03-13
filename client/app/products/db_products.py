
def get_all_active_products(cursor):
    cursor.execute("""
        SELECT p.id, p.name, p.price, c.name AS category
        FROM PRODUCTO p
        JOIN CATEGORIA c ON p.category_id = c.id
        WHERE p.active = 1
    """)
    return cursor.fetchall()

def get_inventory_by_product(cursor, product_id):
    cursor.execute("""
        SELECT s.name, i.quantity
        FROM INVENTARIO i
        JOIN SEDE s ON i.location_id = s.id
        WHERE i.product_id = :product_id
    """, {'product_id': product_id})
    return cursor.fetchall()

def get_product_details(cursor, product_id):
    cursor.execute("""
        SELECT p.id, p.name, p.description, p.price,
            NVL(SUM(i.quantity), 0) AS stock,
            c.name AS category
        FROM PRODUCTO p
        LEFT JOIN INVENTARIO i ON p.id = i.product_id
        JOIN CATEGORIA c ON p.category_id = c.id
        WHERE p.id = :id AND p.active = 1
        GROUP BY p.id, p.name, p.description, p.price, c.name
    """, {'id': product_id})
    return cursor.fetchone()

def get_category_id(cursor, category_name):
    cursor.execute("SELECT id FROM CATEGORIA WHERE name = :category", {'category': category_name})
    return cursor.fetchone()

def get_location_id(cursor, location_name):
    cursor.execute("SELECT id FROM SEDE WHERE name = :location", {'location': location_name})
    return cursor.fetchone()

def insert_product(cursor, sku, name, description, price, slug, category_id, created_at):
    cursor.execute("""
        INSERT INTO PRODUCTO (
            id, sku, name, description, price, slug, active, category_id, created_at, updated_at
        )
        VALUES (
            PRODUCTO_SEQ.NEXTVAL, :sku, :name, :description, :price, :slug, 1, :category_id, :created_at, :created_at
        )
    """, {
        'sku': sku,
        'name': name,
        'description': description,
        'price': price,
        'slug': slug,
        'category_id': category_id,
        'created_at': created_at
    })
    cursor.execute("SELECT PRODUCTO_SEQ.CURRVAL FROM dual")
    return cursor.fetchone()[0]

def insert_inventory(cursor, product_id, location_id, quantity, created_at):
    cursor.execute("""
        INSERT INTO INVENTARIO (id, quantity, product_id, location_id, created_at, updated_at)
        VALUES (INVENTARIO_SEQ.NEXTVAL, :quantity, :product_id, :location_id, :created_at, :created_at)
    """, {
        'quantity': quantity,
        'product_id': product_id,
        'location_id': location_id,
        'created_at': created_at
    })

def update_product_price(cursor, product_id, price, updated_at):
    cursor.execute("""
        UPDATE PRODUCTO SET price = :price, updated_at = :updated_at WHERE id = :id
    """, {
        'price': price,
        'updated_at': updated_at,
        'id': product_id
    })

def get_inventory_entry(cursor, product_id, location_id):
    cursor.execute("""
        SELECT id FROM INVENTARIO
        WHERE product_id = :product_id AND location_id = :location_id
    """, {
        'product_id': product_id,
        'location_id': location_id
    })
    return cursor.fetchone()

def update_inventory(cursor, product_id, location_id, quantity, updated_at):
    cursor.execute("""
        UPDATE INVENTARIO
        SET quantity = :quantity, updated_at = :updated_at
        WHERE product_id = :product_id AND location_id = :location_id
    """, {
        'quantity': quantity,
        'updated_at': updated_at,
        'product_id': product_id,
        'location_id': location_id
    })

def insert_inventory_entry(cursor, product_id, location_id, quantity, created_at):
    cursor.execute("""
        INSERT INTO INVENTARIO (id, quantity, product_id, location_id, created_at, updated_at)
        VALUES (INVENTARIO_SEQ.NEXTVAL, :quantity, :product_id, :location_id, :created_at, :created_at)
    """, {
        'quantity': quantity,
        'product_id': product_id,
        'location_id': location_id,
        'created_at': created_at
    })

def deactivate_product(cursor, product_id, updated_at):
    cursor.execute("""
        UPDATE PRODUCTO SET active = 0, updated_at = :updated_at WHERE id = :id
    """, {
        'updated_at': updated_at,
        'id': product_id
    })