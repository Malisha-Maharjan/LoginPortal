from .config import db, cursor
def get_roles():
    cursor.execute('SELECT * FROM roles')
    return cursor.fetchall()

def get_roles_with_roleid(roleid):
    cursor.execute('SELECT role FROM roles where id=%s', (roleid, )) 
    return cursor.fetchone()