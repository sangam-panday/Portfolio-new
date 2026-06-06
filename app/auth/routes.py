from flask import Blueprint, render_template, request, url_for, redirect

from app.models import User
from app.extension import db

#import hash password
from werkzeug.security import generate_password_hash, check_password_hash

from flask_login import login_required, logout_user, login_user

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('main.app_page'))
        else:
            return render_template('login.html', error='Invalid email or password')

@auth_bp.route('/register', methods = ['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        email = request.form.get('email')
        password = request.form.get('password')

        #email handling
        if email is None or email.strip() == '':
            return render_template('register.html', error='Email cannot be empty')

        #password handling
        if password is None or password.strip() == '':
            return render_template('register.html', error='Password cannot be empty')
        
        elif len(password) < 6:
            return render_template('register.html', error='Password must be at least 6 characters long')

        hashed_password = generate_password_hash(password)
        new_user = User(email=email, password=hashed_password)


        if User.query.filter_by(email=email).first():
            return render_template('register.html', error='Email already exists')
        
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('auth.login'))

@auth_bp.route('/logout')
@login_required  # PROTECT THIS ROUTE
def logout():
    logout_user()  # THIS LOGS THE USER OUT
    return redirect(url_for('main.index'))