from flask import Blueprint, render_template, request, session, url_for, redirect, current_app
from flask_mail import Mail, Message
import os
import random
from app.models import User
from app.extension import db, mail

# import hash password
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
        
        otp =  random.randint(100000, 999999)

        session['otp'] = otp
        session['email'] = email
        session['password'] = hashed_password
        
        # For development: print OTP to console
        print(f"\n{'='*50}")
        print(f"📧 OTP for {email}: {otp}")
        print(f"{'='*50}\n")
        
        # send email

        msg = Message(
            "Email Verification",
            sender=os.getenv('EMAIL_USER'),
            recipients=[email]
        )

        msg.body = f"""
Your OTP is:

{otp}

Valid for verification.
"""

        try:
            mail.send(msg)
        except Exception as e:
            # Log the error but don't fail the registration
            print(f"Email sending failed: {str(e)}")
            # Still proceed with verification - in development, users can use the OTP from logs

        return redirect(
            url_for('auth.verify')
        )
@auth_bp.route('/verify', methods=['GET', 'POST'])
def verify():
    if request.method == 'GET':
        return render_template('verify.html')
    else:
        user_otp = request.form.get('otp')

        if str(user_otp) == str(session.get('otp')):
            new_user = User(email=session.get('email'), password=session.get('password'))
            db.session.add(new_user)
            db.session.commit()

            # Clear session data after successful registration
            session.pop('otp', None)
            session.pop('email', None)
            session.pop('password', None)

            return redirect(url_for('auth.login'))
        else:
            return render_template('verify.html', error='Invalid OTP. Please try again.')

@auth_bp.route('/logout')
@login_required  # PROTECT THIS ROUTE
def logout():
    logout_user()  # THIS LOGS THE USER OUT
    return redirect(url_for('main.index'))