import os
import json
from flask import Blueprint, render_template

policies_bp = Blueprint('policies', __name__)

POLICIES_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'policies.json')


def load_policies():
    try:
        with open(POLICIES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {
            'circulars': [],
            'resolutions': [],
            'memoranda': [],
            'orders': []
        }


def get_category_template(category):
    return {
        'circulars': 'policies/circulars.html',
        'resolutions': 'policies/resolution.html',
        'memoranda': 'policies/memoranda.html',
        'orders': 'policies/office-orders.html',
        'hub': 'policies/policies.html'
    }.get(category, 'policies/policies.html')


@policies_bp.route('/policies/<category>')
def policies_hub(category):
    policies = load_policies()
    category_list = policies.get(category, []) if category in policies else []

    stats = {
        'total': len(category_list),
        'updated': max((p.get('date', '') for p in category_list), default='')
    }

    return render_template(
        get_category_template(category),
        policies=category_list,
        stats=stats,
    )

@policies_bp.route('/reports')
def reports():
    return render_template('policies/reports.html')

@policies_bp.route("/policies")
def policies_index():
    """Render the main policies hub (fallback at /policies)."""
    return render_template("policies/policies.html")

@policies_bp.route("/policies/coming-soon")
def policies_placeholder():
    """Render a themed placeholder page for upcoming policy sections."""
    return render_template("policies/placeholder.html")

@policies_bp.route('/lbp-forms')
def lbp_forms():
    return render_template('policies/lbp-forms.html')
