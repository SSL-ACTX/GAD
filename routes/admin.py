import os
import json
import uuid
from functools import wraps
from datetime import date, datetime
from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, flash

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# ── Path to the events data file ──────────────────────────────────────────────
DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'events.json')

# ── Helpers ────────────────────────────────────────────────────────────────────
def load_events():
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_events(events):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(events, f, indent=2, ensure_ascii=False)

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated

# ── Public API – used by the calendar page ────────────────────────────────────
@admin_bp.route('/api/events')
def api_events():
    return jsonify(load_events())

# ── Auth ──────────────────────────────────────────────────────────────────────
@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('admin_logged_in'):
        return redirect(url_for('admin.dashboard'))
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        admin_user = os.getenv('ADMIN_USERNAME', 'admin')
        admin_pass = os.getenv('ADMIN_PASSWORD', 'gad2026')
        if username == admin_user and password == admin_pass:
            session['admin_logged_in'] = True
            session['admin_user'] = username
            return redirect(url_for('admin.dashboard'))
        else:
            error = 'Invalid username or password.'
    return render_template('admin/login.html', error=error)

@admin_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('admin.login'))

# ── Dashboard ─────────────────────────────────────────────────────────────────
@admin_bp.route('/')
@login_required
def dashboard():
    events = load_events()
    today = date.today().isoformat()
    current_month = date.today().strftime('%Y-%m')
    stats = {
        'total': len(events),
        'upcoming': sum(1 for e in events if e['date'] >= today),
        'this_month': sum(1 for e in events if e['date'].startswith(current_month)),
        'categories': len(set(e['category'] for e in events)),
    }
    # Most recent 5 upcoming events
    upcoming = sorted([e for e in events if e['date'] >= today], key=lambda x: x['date'])[:5]
    return render_template('admin/dashboard.html', stats=stats, upcoming=upcoming)

# ── Events Management ──────────────────────────────────────────────────────────
@admin_bp.route('/events')
@login_required
def events():
    all_events = sorted(load_events(), key=lambda x: x['date'])
    return render_template('admin/events.html', events=all_events)

@admin_bp.route('/events/add', methods=['POST'])
@login_required
def add_event():
    events = load_events()
    new_event = {
        'id': 'e' + str(uuid.uuid4())[:8],
        'date': request.form.get('date', '').strip(),
        'title': request.form.get('title', '').strip(),
        'category': request.form.get('category', 'community').strip(),
        'desc': request.form.get('desc', '').strip(),
    }
    if new_event['date'] and new_event['title']:
        events.append(new_event)
        save_events(events)
        flash('Event added successfully.', 'success')
    else:
        flash('Title and date are required.', 'error')
    return redirect(url_for('admin.events'))

@admin_bp.route('/events/edit/<event_id>', methods=['POST'])
@login_required
def edit_event(event_id):
    events = load_events()
    for ev in events:
        if ev['id'] == event_id:
            ev['title']    = request.form.get('title', ev['title']).strip()
            ev['date']     = request.form.get('date', ev['date']).strip()
            ev['category'] = request.form.get('category', ev['category']).strip()
            ev['desc']     = request.form.get('desc', ev.get('desc', '')).strip()
            break
    save_events(events)
    flash('Event updated.', 'success')
    return redirect(url_for('admin.events'))

@admin_bp.route('/events/delete/<event_id>', methods=['POST'])
@login_required
def delete_event(event_id):
    events = [e for e in load_events() if e['id'] != event_id]
    save_events(events)
    flash('Event deleted.', 'success')
    return redirect(url_for('admin.events'))
