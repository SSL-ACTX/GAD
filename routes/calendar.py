from flask import Blueprint, render_template

calendar_bp = Blueprint('calendar', __name__)

@calendar_bp.route('/calendar')
def calendar_view():
    return render_template('calendar/calendar.html')
