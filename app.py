import mysql.connector
import sys
import re
import os
from flask_wtf.file import FileField, FileAllowed
from flask_wtf import FlaskForm
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, session, flash


UPLOAD_FOLDER = os.path.join('static', 'images')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

db = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="Malisha2001",
    database="greekprofile",
)

cursor = db.cursor(dictionary=True, buffered=True)


app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'your secret key'


@app.route('/')
def hello():
    return render_template('user/index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST':
        try:
            username = request.form['username']
            password = request.form['password']
            cursor.execute(
                'SELECT * FROM accounts a join roles r on a.roleid=r.id WHERE username = %s AND password = %s', (username, password, ))
            account = cursor.fetchone()
            print(account, file=sys.stdout)
            if account:
                session['username'] = username
                session['role'] = account['role']
                msg = 'Logged in successfully'
                return redirect(url_for('admin'))
            else:
                msg = 'Incorrect username/password'
                return render_template('user/login.html', msg=msg)
        except Exception as e:
            msg = e.with_traceback(None)
    else:
        if session.get('username'):
            return redirect(url_for('admin'))
        return render_template('user/login.html', msg=msg)

@app.route('/logout', methods=['GET'])
def logout():
    try:
        session.pop('username')
        return redirect(url_for('login'))
    except Exception as e:
        msg = e.with_traceback(None)


@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST':
        try:
            username = request.form['username']
            password = request.form['password']
            email = request.form['email']
            cursor.execute(
                'SELECT * FROM accounts WHERE username = %s', (username, ))
            account = cursor.fetchone()
            if account:
                msg = 'Account already exist! '
            elif not re.match(r'[A-za-z0-9]+', username):
                msg = 'name must contain only characters and numbers'
            elif not re.match(r'[A-za-z0-9]+@[a-z]+.[a-z]{2,3}', email):
                msg = 'Invalid email'
            else:
                cursor.execute("SELECT id FROM roles WHERE role = 'customer'")
                roles = cursor.fetchone()
                cursor.execute(
                    'INSERT INTO accounts (username, password, email, roleid) VALUES (%s, %s, %s, %s)', (username, password, email, roles['id'], ))
                db.commit()
                msg = 'You have successfully registered.'
        except Exception as e:
            msg = e.with_traceback(None)

    return render_template('user/register.html', msg=msg)


@app.route('/admin')
def admin():
    msg = ''
    if not session.get('username'):
        return redirect(url_for('login'))
    cursor.execute(
        'SELECT * FROM accounts')
    account = cursor.fetchall()
    cursor.execute('SELECT * FROM roles')
    roles = cursor.fetchall()
    return render_template('user/admin.html', account=account, roles=roles)


@app.route('/user')
def user():
    if session['role'] != 'admin':
        return redirect(url_for('unauthorized'))
    cursor.execute('SELECT * FROM accounts')
    account = cursor.fetchall()
    return render_template('user/user.html', account=account)


@app.route('/unauthorized')
def unauthorized():
    return render_template('user/unauthorized.html')

@app.route('/edit/<id>')
def edit(id):
    if session['role'] != 'admin':
        return redirect(url_for('unauthorized'))
    # if request.method == 'GET':
    cursor.execute(
        'SELECT * FROM accounts WHERE id=%s', (id, ))
    account = cursor.fetchone()
    cursor.execute('SELECT * FROM roles')
    roles = cursor.fetchall()
    print(roles, file=sys.stdout)
    return render_template('user/edit.html', account=account, roles=roles)


@app.route('/update', methods=['POST'])
def update():
    if session['role'] != 'admin':
        return redirect(url_for('unauthorized'))
    msg = ''
    username = request.form['username']
    email = request.form['email']
    id = request.form['id']
    roleid = request.form['roleid']
    cursor.execute(
        'SELECT * FROM accounts WHERE username=%s AND id <> %s', (username, id, ))
    account = cursor.fetchone()
    cursor.execute('SELECT * FROM roles')
    roles = cursor.fetchall()
    if account and account['username']:
        msg = 'Username already existed.'
    if account and account['email']:
        msg = 'Email already existed.'
    elif not re.match(r'[A-za-z0-9]+', username):
        msg = 'name must contain only characters and numbers'
    elif not re.match(r'[A-za-z0-9]+@[a-z]+.[a-z]{2,3}', email):
        msg = 'Invalid email'
    else:
        print(id, username, email, roleid, file=sys.stdout)
        cursor.execute('UPDATE accounts SET username=%s, email=%s, roleid=%s WHERE id=%s',
                       (username, email, roleid, id, ))
        db.commit()
        if username == session['username']:
            session['username'] = username
            cursor.execute('SELECT role FROM roles where id=%s', (roleid, )) 
            role = cursor.fetchone()
            if role:
                session['role'] = role
        flash('The record has been successfully updated.')
        return redirect(url_for('user'))
    return render_template('user/edit.html', account=account, msg=msg, roles=roles)


@app.route('/delete/<id>')
def delete(id):
    if session['role'] != 'admin':
        return redirect(url_for('unauthorized'))
    # if request.method == 'GET':
    cursor.execute(
        'SELECT * FROM accounts WHERE id=%s', (id, ))
    account = cursor.fetchone()
    return render_template('user/delete.html', account=account)


@app.route('/destroy', methods=['POST'])
def destroy():
    if session['role'] != 'admin':
        return redirect(url_for('unauthorized'))
    # alert = ''
    print(request.method, file=sys.stdout)
    username = request.form['username']
    cursor.execute('SELECT * FROM accounts WHERE username=%s', (username, ))
    account = cursor.fetchone()
    print('hi', account, file=sys.stdout)
    if account['username'] == session['username']:
        flash("Sorry!")
        return redirect(url_for('user'))
    else:

        cursor.execute('DELETE FROM accounts WHERE username=%s',
                       (username, ))
        flash("Successfully deleted!!")
        db.commit()

        return redirect(url_for('user'))


@app.route('/product')
def product():
    cursor.execute('SELECT * FROM products')
    product = cursor.fetchall()
    print(product, file=sys.stdout)
    return render_template('product/productpage.html', product=product)


@app.route('/add', methods=['POST', 'GET'])
def add():
    if request.method == 'POST':
        productname = request.form['productname']
        price = request.form['price']
        picture = request.files['productimage']
        picture_filename = secure_filename(picture.filename)
        picture.save(os.path.join(
            app.config['UPLOAD_FOLDER'], picture_filename))
        image_path = os.path.join(
            app.config['UPLOAD_FOLDER'], picture_filename)

        cursor.execute(
            'INSERT INTO products (productname, productimage, price) VALUES(%s, %s, %s)', (productname, image_path, price, ))
        db.commit()
        return redirect(url_for('product'))

    return render_template('product/add.html')



@app.route('/productedit/<id>')
def productedit(id):
    cursor.execute('SELECT * FROM products WHERE id=%s', (id, ))
    product = cursor.fetchone()
    
    print(product, file=sys.stdout)
    return render_template('product/productedit.html', product=product)

@app.route('/productupdate', methods=['POST'])
def productupdate():
    id  = request.form['id']
    productname = request.form['productname']
    price = request.form['price']
    picture = request.files['productimage']
    picture_filename = secure_filename(picture.filename)
    image_path = os.path.join(
        app.config['UPLOAD_FOLDER'], picture_filename)
    picture.save(os.path.join(
        app.config['UPLOAD_FOLDER'], picture_filename))
    
    cursor.execute('UPDATE products SET productname=%s, price=%s, productimage=%s WHERE id=%s',
                    (productname, price, image_path, id, ))
    db.commit()
    return redirect(url_for('product'))

@app.route('/deleteproduct/<id>')
def deleteproduct(id):
    # if request.method == 'GET':
    cursor.execute(
        'SELECT * FROM products WHERE id=%s', (id, ))
    product = cursor.fetchone()
    return render_template('product/deleteproduct.html', product=product)


@app.route('/destroyproduct', methods=['POST'])
def destroyproduct():
    # alert = ''
    print(request.method, file=sys.stdout)
    productname = request.form['productname']
    cursor.execute('SELECT * FROM products WHERE productname=%s', (productname, ))
    product = cursor.fetchone()
    print(product, file=sys.stdout)
    cursor.execute('DELETE FROM products WHERE productname=%s',
                    (productname, ))
    flash("Successfully deleted!!")
    db.commit()

    return redirect(url_for('product'))

if __name__ == '__main__':
    app.debug = True
    app.run()
