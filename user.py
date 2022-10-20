import mysql.connector
import sys
import re
import os
from flask_wtf import FlaskForm
from flask import Flask, render_template, request, redirect, url_for, session, flash

db = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="Malisha2001",
    database="greekprofile",
)

cursor = db.cursor(dictionary=True, buffered=True)


app = Flask(__name__)

class login():
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
