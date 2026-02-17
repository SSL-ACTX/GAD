from flask import Blueprint, render_template

legal_bp = Blueprint('legal', __name__)

@legal_bp.route('/legal/privacy-policy')
def privacy_policy():
    return render_template('legal/privacy-policy.html')

@legal_bp.route('/legal/terms-conditions')
def terms_conditions():
    return render_template('legal/terms-conditions.html')

@legal_bp.route('/team/developers')
def developers():
    return render_template('team/developers.html')