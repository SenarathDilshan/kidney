from flask import Blueprint, render_template, redirect, url_for, request, flash
from . import db


from .models import User
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import re

auth = Blueprint("auth", __name__)

@auth.route("/")
@auth.route("/login", methods=['GET', 'POST'], endpoint="login")
def login():
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash("Logged in!", category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Password is incorrect.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html")

@auth.route("/sign-up", methods=['GET', 'POST'], endpoint="sign_up")
def sign_up():
    if request.method == 'POST':
        username = request.form.get("username")
        email = request.form.get("email")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        email_exists = User.query.filter_by(email=email).first()
        username_exists = User.query.filter_by(username=username).first()

        if email_exists:
            flash('Email is already in use.', category='error')
        elif username_exists:
            flash('Username is already in use.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match!', category='error')
        elif len(username) < 2:
            flash('Username is too short.', category='error')
        elif len(password1) < 6:
            flash('Password is too short.', category='error')
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash('Email is invalid.', category='error')
        else:
            new_user = User(email=email, username=username, password=generate_password_hash(password1, method='pbkdf2:sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('User created!', category='success')
            return redirect(url_for('views.home'))

    return render_template("signup.html")

@auth.route("/logout", endpoint="logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))


@auth.route("/admin", methods=['GET', 'POST'], endpoint="admin")
def admin():
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if user:
            if check_password_hash(user.password, password):
                if user.is_admin:  # Assuming you have an is_admin attribute in your User model
                    login_user(user, remember=True)
                    flash("Logged in Admin from auth adminlogin!", category='success')
                    return redirect(url_for('views.dashboard'))  # Change to the dashboard
                else:
                    flash('You do not have admin privileges.', category='error')
            else:
                flash('Password is incorrect.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("adminlogin.html")


@auth.route("/adminsignup", methods=['GET', 'POST'], endpoint="adminsignup")
def adminsignup():
    if request.method == 'POST':
        email = request.form.get("email")
        username = request.form.get("username")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        #is_admin = request.form.get(is_admin)
        is_admin = request.form.get("is_admin") == "on" 

        email_exists = User.query.filter_by(email=email).first()
        username_exists = User.query.filter_by(username=username).first()
        #is_admin = User.query.filter_by(is_admin=True).first()

        if email_exists:
            flash('Email is already in use.', category='error')
        elif username_exists:
            flash('Username is already in use.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match!', category='error')
        elif len(username) < 2:
            flash('Username is too short.', category='error')
        elif len(password1) < 6:
            flash('Password is too short.', category='error')
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash('Email is invalid.', category='error')
        else:
            new_user = User(email=email, username=username, is_admin=True, password=generate_password_hash(password1, method='pbkdf2:sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Admin created!', category='success')
            return redirect(url_for('views.dashboard')) #change to the dashboard

    return render_template("adminsignup.html")

