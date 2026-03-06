from flask import Blueprint, render_template, redirect, url_for, request, session
import os

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login')
def login():
    # Legacy public login route — redirect to admin login
    return redirect(url_for('admin.login'))

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.index'))