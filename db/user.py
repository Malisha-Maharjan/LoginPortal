from .config import db, cursor

def get_all_user():
    cursor.execute('SELECT * FROM accounts')
    return cursor.fetchall()

def get_user_with_role(username, password):
    cursor.execute(
        'SELECT * FROM accounts a join roles r on a.roleid=r.id WHERE username = %s AND password = %s', (username, password, ))
    return cursor.fetchone()

def get_user_by(username):
    cursor.execute('SELECT * FROM accounts WHERE username = %s', (username, )) 
    return cursor.fetchone()

def get_user_id():
    cursor.execute("SELECT id FROM roles WHERE role = 'customer'")
    return cursor.fetchone()

def get_user(id):
    cursor.execute(
        'SELECT * FROM accounts WHERE id=%s', (id, ))
    return cursor.fetchone()

def get_user_with_id(username, id):
    cursor.execute(
        'SELECT * FROM accounts WHERE username=%s AND id <> %s', (username, id, ))
    return cursor.fetchone()

def insert_user(username, password, email):
    roles=get_user_id()
    cursor.execute('INSERT INTO accounts (username, password, email, roleid) VALUES (%s, %s, %s, %s)', (username, password, email, roles['id'], ))
    db.commit()

def update_user(username, email, roleid, id):
    cursor.execute('UPDATE accounts SET username=%s, email=%s, roleid=%s WHERE id=%s',
                       (username, email, roleid, id, ))
    db.commit()

def delete_user(username):
    cursor.execute('DELETE FROM accounts WHERE username=%s',(username, ))
    db.commit()


