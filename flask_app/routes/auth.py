# /exam/flask_app/routes/auth.py

from flask import Blueprint, request, render_template, redirect, session, url_for
from flask_app.database import database

auth_bp = Blueprint('auth', __name__)
db = database()

@auth_bp.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if db.authenticate(email, password):
            session['user'] = email
            return redirect(url_for('events.dashboard'))
        else:
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm = request.form['confirm']

        if password != confirm:
            return render_template('login.html', error='Passwords do not match')
        try:
            db.createUser(email, password)
            return redirect(url_for('auth.login'))
        except Exception as e:
            return render_template('login.html', error=str(e))

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('auth.login'))