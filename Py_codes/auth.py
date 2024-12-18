from flask import Blueprint, flash,render_template, redirect, request, url_for
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from .users_cl import User
from . import db

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        email = request.form.get('email')
        password = request.form.get('password1')

        user = User.query.filter_by(email=email).first()

        if user:
            if check_password_hash(user.password, password):
                flash(f'Good to see you, {user.username}!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('serv.home'))
            else:
                flash('Incorrect password, give it another try!', category='error')
        else:
            flash('This email doesn\'t have an account linked!', category='error')

    return render_template("login.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()

    return redirect(url_for('auth.login'))

@auth.route('/sign_up', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':

        email = request.form.get('email')
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()

        if user:
            flash('Email already has an account linked!', category='error')
        elif len(email) < 8:
            flash('The email should be at least 8 chatacters!', category='error')
        elif len(username) < 5:
            flash('Username should be at least 5 chatacters!', category='error')
        elif password1 != password2:
            flash('Password don\'t match!', category='error')
        elif len(password1) < 4:
            flash('Password should be at least 4 chatacters!', category='error')
        else:
            new_user = User(email=email, username=username, password=generate_password_hash(password1, method='pbkdf2:sha256'))
            db.session.add(new_user)
            db.session.commit()
            flash('The account was created with success!', category='success')
            return redirect(url_for('serv.home'))

    return render_template("sign_up.html", user=current_user)