from .config import db, cursor

def get_product():
    cursor.execute('SELECT * FROM products')
    return cursor.fetchall()   

def get_product_with_id(id):
    cursor.execute('SELECT * FROM products WHERE id=%s', (id, ))
    return cursor.fetchone()

def get_product_with_name(productname):
    cursor.execute('SELECT * FROM products WHERE productname=%s', (productname, ))
    return cursor.fetchone()

def insert_product(productname, image_path, price):
    cursor.execute(
        'INSERT INTO products (productname, productimage, price) VALUES(%s, %s, %s)', (productname, image_path, price, ))
    db.commit() 

def update_product(productname, price, image_path, id):
    cursor.execute('UPDATE products SET productname=%s, price=%s, productimage=%s WHERE id=%s',
                    (productname, price, image_path, id, ))
    db.commit()

def delete_product(productname):
    cursor.execute('DELETE FROM products WHERE productname=%s',
                    (productname, ))
    db.commit()