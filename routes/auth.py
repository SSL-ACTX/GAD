from flask import Blueprint, render_template, redirect, url_for

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login')
def login():
    # Future login logic
    return "Login Page Coming Soon"

@auth_bp.route('/logout')
def logout():
    return redirect(url_for('main.index'))