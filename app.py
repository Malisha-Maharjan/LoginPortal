import mysql.connector
import sys
import re
import os
from flask_wtf.file import FileField, FileAllowed
from flask_wtf import FlaskForm
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, session, flash

from db.user import get_user_with_role, get_user_by, get_user_id, get_all_user, get_user, get_user_with_id 
from db.user import insert_user, update_user, delete_user
from db.role import get_roles, get_roles_with_roleid
from db.product import get_product, get_product_with_id, get_product_with_name
from db.product import insert_product, update_product, delete_product

UPLOAD_FOLDER = os.path.join('static', 'images')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


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
            print(username, file=sys.stdout)
            account = get_user_with_role(username, password)
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
            account = get_user_by(username)
            if account:
                msg = 'Account already exist! '
            elif not re.match(r'[A-za-z0-9]+', username):
                msg = 'name must contain only characters and numbers'
            elif not re.match(r'[A-za-z0-9]+@[a-z]+.[a-z]{2,3}', email):
                msg = 'Invalid email'
            else:
                insert_user(username, password, email)
                msg = 'You have successfully registered.'
        except Exception as e:
            msg = e.with_traceback(None)
    return render_template('user/register.html', msg=msg)



@app.route('/admin')
def admin():
    msg = ''
    if not session.get('username'):
        return redirect(url_for('login'))
    return render_template('user/admin.html')


@app.route('/user')
def user():
    if session['role'] != 'admin':
        return redirect(url_for('unauthorized'))
    account = get_all_user()
    return render_template('user/user.html', account=account)


@app.route('/unauthorized')
def unauthorized():
    return render_template('user/unauthorized.html')

@app.route('/edit/<id>')
def edit(id):
    if session['role'] != 'admin':
        return redirect(url_for('unauthorized'))
    account = get_user(id)
    roles = get_roles()
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
    account = get_user_with_id(username, id)
    roles = get_roles()
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
        update_user(username, email, roleid, id)
        if username == session['username']:
            session['username'] = username
            role = get_roles_with_roleid(roleid)
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
    account = get_user(id)
    return render_template('user/delete.html', account=account)


@app.route('/destroy', methods=['POST'])
def destroy():
    if session['role'] != 'admin':
        return redirect(url_for('unauthorized'))
    print(request.method, file=sys.stdout)
    username = request.form['username']
    account = get_user_by(username)
    print('hi', account, file=sys.stdout)
    if account['username'] == session['username']:
        flash("Sorry!")
        return redirect(url_for('user'))
    else:
        delete_user(username)
        flash("Successfully deleted!!")
        return redirect(url_for('user'))


@app.route('/product')
def product():
    product = get_product()
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
        insert_product(productname, image_path, price)
        return redirect(url_for('product'))

    return render_template('product/add.html')


@app.route('/productedit/<id>')
def productedit(id):
    product = get_product_with_id(id)
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
    picture.save(image_path)
    
    update_product(productname, price, image_path, id)
    return redirect(url_for('product'))

@app.route('/deleteproduct/<id>')
def deleteproduct(id):
    product = get_product_with_id(id)
    return render_template('product/deleteproduct.html', product=product)


@app.route('/destroyproduct', methods=['POST'])
def destroyproduct():
    print(request.method, file=sys.stdout)
    productname = request.form['productname']
    product = get_product_with_name(productname)
    print(product, file=sys.stdout)
    delete_product(productname)
    flash("Successfully deleted!!")

    return redirect(url_for('product'))

if __name__ == '__main__':
    app.debug = True
    app.run()
