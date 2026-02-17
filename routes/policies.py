from flask import Blueprint, render_template

policies_bp = Blueprint('policies', __name__)

@policies_bp.route('/policies/<category>')
def policies_hub(category):
    template_map = {
        'circulars': 'policies/circulars.html',
        'resolutions': 'policies/resolution.html',
        'memoranda': 'policies/memoranda.html',
        'orders': 'policies/office-orders.html',
        'hub': 'policies/policies.html'
    }
    target_template = template_map.get(category, 'policies/policies.html')
    return render_template(target_template)

@policies_bp.route('/reports')
def reports():
    return render_template('policies/reports.html')