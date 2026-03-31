import os
import json
import uuid
import subprocess
from functools import wraps
from datetime import date, datetime
from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, flash
from werkzeug.utils import secure_filename

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# ── Data file paths ───────────────────────────────────────────────────────────
DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'events.json')
PROJECTS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'projects.json')
POLICIES_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'policies.json')
KNOWLEDGE_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'knowledge_products.json')
BROCHURES_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'brochures.json')
LIVELIHOOD_FEEDS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'livelihood_feeds.json')
ORG_STRUCTURE_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'org_structure.json')
COMMITTEE_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'committee.json')
TRACKING_MATRIX_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'tracking_matrix.json')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'pdf', 'docx', 'doc', 'mp4', 'webm', 'ogg'}
POLICIES_UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads', 'policies')
PROJECTS_UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads', 'projects')
KNOWLEDGE_UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads', 'knowledge')
BROCHURES_UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads', 'brochures')
LIVELIHOOD_UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads', 'livelihood')
COMMITTEE_UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads', 'committee')
ORG_UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads', 'org')

# ── Site Config ───────────────────────────────────────────────────────────────
SITE_CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'site_config.json')


def load_site_config():
    default = {
        'policies': {'start_year': 2002, 'current_year': datetime.now().year},
        'reports': {'years': ['2024', '2023', '2022', '2021', '2020']}
    }
    try:
        with open(SITE_CONFIG_FILE, 'r', encoding='utf-8') as f:
            raw = json.load(f)
            if not isinstance(raw, dict):
                return default
            merged = default.copy()
            merged.update(raw)
            merged['policies'] = {**default['policies'], **(raw.get('policies') or {})}
            merged['reports'] = {**default['reports'], **(raw.get('reports') or {})}
            return merged
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def save_site_config(config):
    os.makedirs(os.path.dirname(SITE_CONFIG_FILE), exist_ok=True)
    with open(SITE_CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


# ── Helpers ────────────────────────────────────────────────────────────────────
def load_events():
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def load_policies():
    try:
        with open(POLICIES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {'republic_acts': [], 'memoranda': [], 'resolutions': [], 'orders': [], 'lbp_forms': [], 'reports': []}


def save_policies(policies):
    os.makedirs(os.path.dirname(POLICIES_FILE), exist_ok=True)
    with open(POLICIES_FILE, 'w', encoding='utf-8') as f:
        json.dump(policies, f, indent=2, ensure_ascii=False)

def save_events(events):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(events, f, indent=2, ensure_ascii=False)

def load_projects():
    try:
        with open(PROJECTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_projects(projects):
    os.makedirs(os.path.dirname(PROJECTS_FILE), exist_ok=True)
    with open(PROJECTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(projects, f, indent=2, ensure_ascii=False)

def load_knowledge_products():
    try:
        with open(KNOWLEDGE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_knowledge_products(products):
    os.makedirs(os.path.dirname(KNOWLEDGE_FILE), exist_ok=True)
    with open(KNOWLEDGE_FILE, 'w', encoding='utf-8') as f:
        json.dump(products, f, indent=2, ensure_ascii=False)

def load_brochures():
    try:
        with open(BROCHURES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_brochures(brochures):
    os.makedirs(os.path.dirname(BROCHURES_FILE), exist_ok=True)
    with open(BROCHURES_FILE, 'w', encoding='utf-8') as f:
        json.dump(brochures, f, indent=2, ensure_ascii=False)

def load_livelihood_feeds():
    try:
        with open(LIVELIHOOD_FEEDS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_livelihood_feeds(feeds):
    os.makedirs(os.path.dirname(LIVELIHOOD_FEEDS_FILE), exist_ok=True)
    with open(LIVELIHOOD_FEEDS_FILE, 'w', encoding='utf-8') as f:
        json.dump(feeds, f, indent=2, ensure_ascii=False)

def load_org_structure():
    try:
        with open(ORG_STRUCTURE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {
            "chart_image": "", 
            "pdf_url": "", 
            "manual_url": "",
            "components": [
                {
                    "title": "Executive Committee",
                    "description": "Chaired by the Local Chief Executive, this body is responsible for policy direction and high-level strategic planning of all GAD initiatives within the municipality."
                },
                {
                    "title": "Technical Working Group",
                    "description": "The TWG translates policies into action, assisting in the preparation of the GAD Plan and Budget, and managing day-to-day implementation."
                }
            ]
        }

def save_org_structure(data):
    os.makedirs(os.path.dirname(ORG_STRUCTURE_FILE), exist_ok=True)
    with open(ORG_STRUCTURE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_committee():
    try:
        with open(COMMITTEE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_committee(committee):
    os.makedirs(os.path.dirname(COMMITTEE_FILE), exist_ok=True)
    with open(COMMITTEE_FILE, 'w', encoding='utf-8') as f:
        json.dump(committee, f, indent=2, ensure_ascii=False)

def load_tracking_matrix():
    try:
        with open(TRACKING_MATRIX_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_tracking_matrix(data):
    os.makedirs(os.path.dirname(TRACKING_MATRIX_FILE), exist_ok=True)
    with open(TRACKING_MATRIX_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def log_tracking(corner, entry_type, description, technical_officer=None):
    from datetime import datetime
    try:
        from flask import request, session
        if not technical_officer and request and request.form:
            technical_officer = request.form.get('technical_officer', '').strip()
    except Exception:
        pass
        
    now = datetime.now()
    
    # Simple am/pm formatting logic to remove leading zero
    hour_12 = now.strftime('%I').lstrip('0') or '12'
    time_str = f"{hour_12}:{now.strftime('%M %p')}"
    
    date_str = now.strftime('%B %d, %Y')
    
    entries = load_tracking_matrix()
    entries.insert(0, {
        'id': 'trk' + str(uuid.uuid4())[:8],
        'corner': corner,
        'date': date_str,
        'time_started': time_str,
        'time_completed': time_str,
        'type': entry_type,
        'description': description,
        'updates_posted': f"{date_str}, {time_str}",
        'technical_officer': technical_officer or session.get('admin_user', 'System')
    })
    save_tracking_matrix(entries)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file, folder_path, prefix="p"):
    """Generic helper to save an uploaded file."""
    if file and file.filename and allowed_file(file.filename):
        os.makedirs(folder_path, exist_ok=True)
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{prefix}_{str(uuid.uuid4())[:8]}.{ext}"
        file.save(os.path.join(folder_path, filename))
        
        # Determine the web-accessible path fragments
        # For simplicity, we assume everything is under 'static/'
        parts = folder_path.replace('\\', '/').split('/')
        if 'static' in parts:
            static_idx = parts.index('static')
            return '/'.join(parts[static_idx+1:]) + '/' + filename
    return None

def save_uploaded_image(file):
    return save_uploaded_file(file, PROJECTS_UPLOAD_FOLDER, prefix="proj")

def save_policy_pdf(file):
    return save_uploaded_file(file, POLICIES_UPLOAD_FOLDER, prefix="memo")

def save_knowledge_asset(file):
    return save_uploaded_file(file, KNOWLEDGE_UPLOAD_FOLDER, prefix="kp")

def save_video(file):
    return save_uploaded_file(file, POLICIES_UPLOAD_FOLDER, prefix="vid")

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

# ── System Features ───────────────────────────────────────────────────────────
@admin_bp.route('/features')
@login_required
def features():
    schedule_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'scraper_schedule.json')
    schedule_config = {"enabled": False, "hour": "2", "minute": "0"}
    try:
        if os.path.exists(schedule_file):
            with open(schedule_file, 'r') as f:
                schedule_config = json.load(f)
    except Exception:
        pass
        
    carousel_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'carousel.json')
    carousel_images = []
    try:
        if os.path.exists(carousel_file):
            with open(carousel_file, 'r') as f:
                carousel_images = json.load(f)
    except Exception:
        pass
    
    site_config = load_site_config()
    return render_template('admin/features.html', schedule=schedule_config, carousel_images=carousel_images, site_config=site_config)

@admin_bp.route('/policies')
@login_required
def policies_settings():
    """Admin UI for managing policy entries and config."""
    site_config = load_site_config()
    policies = load_policies()
    return render_template('admin/policies.html', site_config=site_config, policies=policies)


@admin_bp.route('/policies/add', methods=['POST'])
@login_required
def add_policy_entry():
    policies = load_policies()
    site_config = load_site_config()
    category = request.form.get('category', 'circulars')
    year_default = site_config.get('policies', {}).get('current_year', datetime.now().year)
    try:
        year = int(request.form.get('year', year_default))
    except ValueError:
        year = year_default

    # Handle File Upload
    uploaded_file = request.files.get('policy_file')
    file_path = save_policy_pdf(uploaded_file)
    if not file_path:
        file_path = request.form.get('file', '').strip() or '#'

    # Handle Video Upload
    uploaded_video = request.files.get('video_file')
    video_path = save_video(uploaded_video)
    if not video_path:
        video_path = request.form.get('video_path', '').strip()

    entry = {
        'id': 'p' + str(uuid.uuid4())[:8],
        'year': year,
        'title': request.form.get('title', '').strip(),
        'description': request.form.get('description', '').strip(),
        'date': request.form.get('date', '').strip(),
        'status': request.form.get('status', '').strip() or 'Active',
        'file': file_path,
        'url': request.form.get('url', '').strip(),
        'video_file': video_path,
        'video_url': request.form.get('video_url', '').strip()
    }
    policies.setdefault(category, []).insert(0, entry)
    save_policies(policies)
    log_tracking("Digital", "Policy", f"Added new policy: {entry['title']}")
    flash('Policy entry added.', 'success')
    return redirect(url_for('admin.policies_settings'))


@admin_bp.route('/policies/edit/<entry_id>', methods=['POST'])
@login_required
def edit_policy_entry(entry_id):
    policies = load_policies()

    old_category = None
    old_index = -1
    old_entry = None
    for cat, entries in policies.items():
        for idx, entry in enumerate(entries):
            if entry.get('id') == entry_id:
                old_category = cat
                old_index = idx
                old_entry = entry
                break
        if old_entry:
            break

    if not old_entry:
        flash('Policy entry not found.', 'error')
        return redirect(url_for('admin.policies_settings'))

    new_category = request.form.get('category', old_category)
    try:
        year = int(request.form.get('year', old_entry.get('year', datetime.now().year)))
    except ValueError:
        year = old_entry.get('year', datetime.now().year)

    # Handle File Upload
    uploaded_file = request.files.get('policy_file')
    file_path = save_policy_pdf(uploaded_file)
    if not file_path:
        file_path = request.form.get('file', old_entry.get('file', '#')).strip() or '#'

    # Handle Video Upload
    uploaded_video = request.files.get('video_file')
    video_path = save_video(uploaded_video)
    if not video_path:
        video_path = request.form.get('video_path', old_entry.get('video_file', '')).strip()

    updated_entry = {
        'id': entry_id,
        'year': year,
        'title': request.form.get('title', old_entry.get('title', '')).strip(),
        'description': request.form.get('description', old_entry.get('description', '')).strip(),
        'date': request.form.get('date', old_entry.get('date', '')).strip(),
        'status': request.form.get('status', old_entry.get('status', 'Active')).strip() or 'Active',
        'file': file_path,
        'url': request.form.get('url', old_entry.get('url', '')).strip(),
        'video_file': video_path,
        'video_url': request.form.get('video_url', old_entry.get('video_url', '')).strip()
    }

    # Remove from original category first.
    policies[old_category].pop(old_index)

    # Reinsert into target category.
    policies.setdefault(new_category, [])
    if new_category == old_category:
        policies[new_category].insert(old_index, updated_entry)
    else:
        policies[new_category].insert(0, updated_entry)

    save_policies(policies)
    log_tracking("Digital", "Policy", f"Updated policy: {updated_entry['title']}")
    flash('Policy entry updated.', 'success')
    return redirect(url_for('admin.policies_settings'))


@admin_bp.route('/policies/delete/<entry_id>', methods=['POST'])
@login_required
def delete_policy_entry(entry_id):
    policies = load_policies()
    changed = False
    for cat, entries in policies.items():
        new_entries = [e for e in entries if e.get('id') != entry_id]
        if len(new_entries) != len(entries):
            policies[cat] = new_entries
            changed = True
    if changed:
        save_policies(policies)
        log_tracking("Digital", "Policy", "Deleted a policy entry")
        flash('Policy entry deleted.', 'success')
    else:
        flash('Policy entry not found.', 'error')
    return redirect(url_for('admin.policies_settings'))


@admin_bp.route('/save_carousel', methods=['POST'])
@login_required
def save_carousel():
    urls = request.form.getlist('urls[]')
    # filter blanks
    urls = [u.strip() for u in urls if u.strip()]
    
    carousel_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'carousel.json')
    try:
        with open(carousel_file, 'w') as f:
            json.dump(urls, f, indent=4)
        flash('Carousel images updated successfully.', 'success')
    except Exception as e:
        flash(f'Failed to update carousel: {e}', 'error')
        
    return redirect(url_for('admin.features'))

@admin_bp.route('/configure_scraper', methods=['POST'])
@login_required
def configure_scraper():
    enabled = request.form.get('enabled') == 'on'
    hour = request.form.get('hour', '2').strip()
    minute = request.form.get('minute', '0').strip()
    
    schedule_config = {
        "enabled": enabled,
        "hour": hour,
        "minute": minute
    }
    
    schedule_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'scraper_schedule.json')
    try:
        with open(schedule_file, 'w') as f:
            json.dump(schedule_config, f)
        
        # We need to tell the main app to reload the schedule. 
        # In a real production deployment with multiple workers, we'd use a database or Redis for this.
        # But for this simple app, we can just let it restart or wait for Wzeug reload if in dev.
        # However, a cleaner way is just importing the scheduler here and updating it, but since
        # it's defined in app.py we might get circular imports.
        # For simplicity, we'll just save it and let the next app start pick it up, 
        # OR we can try to do a local update if we move the scheduler init.
        # The prompt asked for a simple scheduler so saving to JSON and notifying user it requires restart
        # OR we can just try to import app and scheduler. Let's just flash a message.
        from app import setup_scheduler
        setup_scheduler() # This will dynamically update the scheduler in the current process!
        
        if enabled:
            flash(f'Scraper schedule saved and enabled for {hour.zfill(2)}:{minute.zfill(2)} everyday.', 'success')
        else:
            flash('Scraper schedule saved and disabled.', 'success')
            
    except Exception as e:
        flash(f'Failed to save schedule: {e}', 'error')
        
    return redirect(url_for('admin.features'))

@admin_bp.route('/save_site_config', methods=['POST'], endpoint='save_site_config')
@login_required
def save_site_config_route():
    """Save site configuration (policies/reports) from the admin features page."""
    config = load_site_config()
    policies = config.get('policies', {})
    reports = config.get('reports', {})

    # Policies settings
    try:
        policies['start_year'] = int(request.form.get('policies_start_year', policies.get('start_year', 2002)))
    except ValueError:
        policies['start_year'] = policies.get('start_year', 2002)

    try:
        policies['current_year'] = int(request.form.get('policies_current_year', policies.get('current_year', datetime.now().year)))
    except ValueError:
        policies['current_year'] = policies.get('current_year', datetime.now().year)

    # Reports settings (comma separated list)
    raw_years = request.form.get('reports_years', '')
    years = [y.strip() for y in raw_years.split(',') if y.strip()]
    if years:
        reports['years'] = years

    config['policies'] = policies
    config['reports'] = reports

    try:
        save_site_config(config)
        flash('Site configuration saved successfully.', 'success')
    except Exception as e:
        flash(f'Failed to save site settings: {e}', 'error')

    return redirect(url_for('admin.policies_settings'))


@admin_bp.route('/scrape_news', methods=['POST'])
@login_required
def scrape_news():
    try:
        script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scripts', 'scrape_news.py')
        # Run scraper script and wait for completion
        subprocess.run(['python', script_path], check=True)
        flash('News scraper completed successfully. Homepage is updated.', 'success')
    except subprocess.CalledProcessError as e:
        flash(f'Error running scraper. It may have failed or timed out.', 'error')
    except Exception as e:
        flash(f'An unexpected error occurred: {str(e)}', 'error')
    
    return redirect(url_for('admin.features'))

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
        log_tracking("Digital", "Event", f"Added new event: {new_event['title']}")
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
    log_tracking("Digital", "Event", "Updated an event")
    flash('Event updated.', 'success')
    return redirect(url_for('admin.events'))

@admin_bp.route('/events/delete/<event_id>', methods=['POST'])
@login_required
def delete_event(event_id):
    events = [e for e in load_events() if e['id'] != event_id]
    save_events(events)
    log_tracking("Digital", "Event", "Deleted an event")
    flash('Event deleted.', 'success')
    return redirect(url_for('admin.events'))

# ── Project Archives Management ───────────────────────────────────────────────
@admin_bp.route('/projects')
@login_required
def projects():
    all_projects = load_projects()
    years = sorted(set(p.get('year', '') for p in all_projects), reverse=True)
    total = len(all_projects)
    return render_template('admin/projects.html', projects=all_projects, years=years, total=total)

@admin_bp.route('/projects/add', methods=['POST'])
@login_required
def add_project():
    all_projects = load_projects()
    image_path = save_uploaded_image(request.files.get('image'))
    new_project = {
        'id': 'p' + str(uuid.uuid4())[:8],
        'year': request.form.get('year', '').strip(),
        'title': request.form.get('title', '').strip(),
        'category': request.form.get('category', '').strip(),
        'description': request.form.get('description', '').strip(),
        'status': request.form.get('status', 'Ongoing').strip(),
        'image': image_path,
    }
    if new_project['title'] and new_project['year']:
        all_projects.append(new_project)
        save_projects(all_projects)
        log_tracking("Digital", "Project Archive", f"Added project: {new_project['title']}")
        flash('Project added successfully.', 'success')
    else:
        flash('Title and year are required.', 'error')
    return redirect(url_for('admin.projects'))

@admin_bp.route('/projects/edit/<project_id>', methods=['POST'])
@login_required
def edit_project(project_id):
    all_projects = load_projects()
    for p in all_projects:
        if p['id'] == project_id:
            p['year'] = request.form.get('year', p['year']).strip()
            p['title'] = request.form.get('title', p['title']).strip()
            p['category'] = request.form.get('category', p.get('category', '')).strip()
            p['description'] = request.form.get('description', p.get('description', '')).strip()
            p['status'] = request.form.get('status', p.get('status', 'Ongoing')).strip()
            new_image = save_uploaded_image(request.files.get('image'))
            if new_image:
                # Delete old image if exists
                if p.get('image'):
                    old_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', p['image'])
                    if os.path.exists(old_path):
                        os.remove(old_path)
                p['image'] = new_image
            break
    save_projects(all_projects)
    log_tracking("Digital", "Project Archive", "Updated a project in the archives")
    flash('Project updated.', 'success')
    return redirect(url_for('admin.projects'))

@admin_bp.route('/projects/delete/<project_id>', methods=['POST'])
@login_required
def delete_project(project_id):
    all_projects = load_projects()
    project = next((p for p in all_projects if p['id'] == project_id), None)
    if project and project.get('image'):
        old_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', project['image'])
        if os.path.exists(old_path):
            os.remove(old_path)
    all_projects = [p for p in all_projects if p['id'] != project_id]
    save_projects(all_projects)
    log_tracking("Digital", "Project Archive", "Deleted a project from the archives")
    flash('Project deleted.', 'success')
    return redirect(url_for('admin.projects'))

# ── Knowledge Products Management ───────────────────────────────────────────
@admin_bp.route('/knowledge')
@login_required
def knowledge():
    items = load_knowledge_products()
    return render_template('admin/knowledge.html', items=items)

@admin_bp.route('/knowledge/add', methods=['POST'])
@login_required
def add_knowledge_entry():
    items = load_knowledge_products()
    image_path = save_knowledge_asset(request.files.get('image'))
    file_path = save_knowledge_asset(request.files.get('file'))
    
    new_item = {
        'id': 'kp' + str(uuid.uuid4())[:8],
        'title': request.form.get('title', '').strip(),
        'description': request.form.get('description', '').strip(),
        'type': request.form.get('type', 'Material').strip(),
        'date': request.form.get('date', '').strip(),
        'image': image_path or request.form.get('image_url', ''),
        'file': file_path or request.form.get('file_url', '#'),
        'url': request.form.get('url', '').strip(),
        'action_text': request.form.get('action_text', 'View Document').strip()
    }
    
    if new_item['title']:
        items.insert(0, new_item)
        save_knowledge_products(items)
        log_tracking("Digital", "Knowledge Product", f"Added new knowledge product: {new_item['title']}")
        flash('Knowledge Product added successfully.', 'success')
    return redirect(url_for('admin.knowledge'))

@admin_bp.route('/knowledge/edit/<item_id>', methods=['POST'])
@login_required
def edit_knowledge_entry(item_id):
    items = load_knowledge_products()
    for item in items:
        if item['id'] == item_id:
            item['title'] = request.form.get('title', item['title']).strip()
            item['description'] = request.form.get('description', item.get('description', '')).strip()
            item['type'] = request.form.get('type', item.get('type', 'Material')).strip()
            item['date'] = request.form.get('date', item.get('date', '')).strip()
            item['action_text'] = request.form.get('action_text', item.get('action_text', 'View Document')).strip()
            item['url'] = request.form.get('url', item.get('url', '')).strip()
            
            new_image = save_knowledge_asset(request.files.get('image'))
            if new_image:
                item['image'] = new_image
            else:
                item['image'] = request.form.get('image_url', item.get('image', ''))

            new_file = save_knowledge_asset(request.files.get('file'))
            if new_file:
                item['file'] = new_file
            else:
                item['file'] = request.form.get('file_url', item.get('file', '#'))
            break
            
    save_knowledge_products(items)
    log_tracking("Digital", "Knowledge Product", "Updated a knowledge product")
    flash('Knowledge Product updated.', 'success')
    return redirect(url_for('admin.knowledge'))

@admin_bp.route('/knowledge/delete/<item_id>', methods=['POST'])
@login_required
def delete_knowledge_entry(item_id):
    all_items = [i for i in load_knowledge_products() if i['id'] != item_id]
    save_knowledge_products(all_items)
    log_tracking("Digital", "Knowledge Product", "Deleted a knowledge product")
    flash('Knowledge Product deleted.', 'success')
    return redirect(url_for('admin.knowledge'))

# ── Brochures Management ──────────────────────────────────────────────────
@admin_bp.route('/brochures')
@login_required
def brochures():
    items = load_brochures()
    return render_template('admin/brochures.html', items=items)

@admin_bp.route('/brochures/add', methods=['POST'])
@login_required
def add_brochure():
    items = load_brochures()
    file_path = ""
    
    # Handle file upload if present
    if 'file' in request.files:
        file = request.files['file']
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            unique_name = f"{str(uuid.uuid4())[:8]}_{filename}"
            os.makedirs(BROCHURES_UPLOAD_FOLDER, exist_ok=True)
            file.save(os.path.join(BROCHURES_UPLOAD_FOLDER, unique_name))
            file_path = f"uploads/brochures/{unique_name}"
            
    new_item = {
        'id': 'br' + str(uuid.uuid4())[:8],
        'title': request.form.get('title', '').strip(),
        'url': request.form.get('url', '').strip(),
        'file': file_path or request.form.get('file_url', '#')
    }
    
    if new_item['title']:
        items.append(new_item)
        save_brochures(items)
        log_tracking("Digital", "Brochure", f"Added new brochure: {new_item['title']}")
        flash('Brochure added successfully.', 'success')
    return redirect(url_for('admin.brochures'))

@admin_bp.route('/brochures/edit/<item_id>', methods=['POST'])
@login_required
def edit_brochure(item_id):
    items = load_brochures()
    for item in items:
        if item['id'] == item_id:
            item['title'] = request.form.get('title', item['title']).strip()
            item['url'] = request.form.get('url', item.get('url', '')).strip()
            
            if 'file' in request.files:
                file = request.files['file']
                if file and file.filename != '':
                    filename = secure_filename(file.filename)
                    unique_name = f"{str(uuid.uuid4())[:8]}_{filename}"
                    os.makedirs(BROCHURES_UPLOAD_FOLDER, exist_ok=True)
                    file.save(os.path.join(BROCHURES_UPLOAD_FOLDER, unique_name))
                    item['file'] = f"uploads/brochures/{unique_name}"
                else:
                    item['file'] = request.form.get('file_url', item.get('file', '#'))
            break
            
    save_brochures(items)
    log_tracking("Digital", "Brochure", "Updated a brochure")
    flash('Brochure updated.', 'success')
    return redirect(url_for('admin.brochures'))

@admin_bp.route('/brochures/delete/<item_id>', methods=['POST'])
@login_required
def delete_brochure(item_id):
    items = [i for i in load_brochures() if i['id'] != item_id]
    save_brochures(items)
    log_tracking("Digital", "Brochure", "Deleted a brochure")
    flash('Brochure deleted.', 'success')
    return redirect(url_for('admin.brochures'))

# ── Livelihood Feeds Management ──────────────────────────────────────────
@admin_bp.route('/livelihood-feeds')
@login_required
def livelihood_feeds():
    items = load_livelihood_feeds()
    return render_template('admin/livelihood_feeds.html', items=items)

@admin_bp.route('/livelihood-feeds/add', methods=['POST'])
@login_required
def add_livelihood_feed():
    items = load_livelihood_feeds()
    
    file_path = ""
    if 'file' in request.files:
        file = request.files['file']
        if file and file.filename:
            file_path = save_uploaded_file(file, LIVELIHOOD_UPLOAD_FOLDER, prefix="lf")

    new_item = {
        'id': 'lf' + str(uuid.uuid4())[:8],
        'title': request.form.get('title', '').strip(),
        'description': request.form.get('description', '').strip(),
        'type': request.form.get('type', 'facebook').strip(),
        'url': request.form.get('url', '').strip(),
        'file': file_path,
        'date': request.form.get('date', '').strip() or date.today().isoformat()
    }
    
    if new_item['title'] or new_item['url'] or new_item['file']:
        items.insert(0, new_item)
        save_livelihood_feeds(items)
        log_tracking("Digital", "Livelihood Feed", f"Added livelihood feed: {new_item.get('title', 'Unknown')}")
        flash('Livelihood Feed added successfully.', 'success')
    return redirect(url_for('admin.livelihood_feeds'))

@admin_bp.route('/livelihood-feeds/edit/<feed_id>', methods=['POST'])
@login_required
def edit_livelihood_feed(feed_id):
    items = load_livelihood_feeds()
    for item in items:
        if item['id'] == feed_id:
            item['title'] = request.form.get('title', item.get('title', '')).strip()
            item['description'] = request.form.get('description', item.get('description', '')).strip()
            item['type'] = request.form.get('type', item.get('type', 'facebook')).strip()
            item['url'] = request.form.get('url', item.get('url', '')).strip()
            item['date'] = request.form.get('date', item.get('date', '')).strip()
            
            if 'file' in request.files:
                file = request.files['file']
                if file and file.filename:
                    new_file = save_uploaded_file(file, LIVELIHOOD_UPLOAD_FOLDER, prefix="lf")
                    if new_file:
                        item['file'] = new_file
            break
            
    save_livelihood_feeds(items)
    log_tracking("Digital", "Livelihood Feed", "Updated a livelihood feed")
    flash('Livelihood Feed updated.', 'success')
    return redirect(url_for('admin.livelihood_feeds'))

@admin_bp.route('/livelihood-feeds/delete/<feed_id>', methods=['POST'])
@login_required
def delete_livelihood_feed(feed_id):
    items = [i for i in load_livelihood_feeds() if i['id'] != feed_id]
    save_livelihood_feeds(items)
    log_tracking("Digital", "Livelihood Feed", "Deleted a livelihood feed")
    flash('Feed deleted.', 'success')
    return redirect(url_for('admin.livelihood_feeds'))

# ── GFPS Structure Management ─────────────────────────────────────────
@admin_bp.route('/org-structure', endpoint='org_structure')
@login_required
def gfps_structure():
    data = load_org_structure()
    return render_template('admin/org_structure.html', data=data)

@admin_bp.route('/org-structure/update', methods=['POST'])
@login_required
def update_org_structure():
    data = load_org_structure()
    
    if 'chart_image' in request.files:
        file = request.files['chart_image']
        if file and file.filename:
            path = save_uploaded_file(file, ORG_UPLOAD_FOLDER, prefix="chart")
            if path: data['chart_image'] = path
            
    if 'pdf' in request.files:
        file = request.files['pdf']
        if file and file.filename:
            path = save_uploaded_file(file, ORG_UPLOAD_FOLDER, prefix="pdf")
            if path: data['pdf_url'] = path
            
    if 'manual' in request.files:
        file = request.files['manual']
        if file and file.filename:
            path = save_uploaded_file(file, ORG_UPLOAD_FOLDER, prefix="manual")
            if path: data['manual_url'] = path
            
    # Dynamic GFPS Components
    component_titles = request.form.getlist('component_titles[]')
    component_descs = request.form.getlist('component_descs[]')
    
    components = []
    for title, desc in zip(component_titles, component_descs):
        if title.strip() or desc.strip():
            components.append({
                "title": title.strip(),
                "description": desc.strip()
            })
    
    data['components'] = components
            
    save_org_structure(data)
    log_tracking("Digital", "Organization Structure", "Updated the Organizational chart of the GFPS")
    flash('Organization structure updated.', 'success')
    return redirect(url_for('admin.org_structure'))

# ── GFPS Committee Management ─────────────────────────────────────────
@admin_bp.route('/committee', endpoint='committee')
@login_required
def gfps_committee():
    members = load_committee()
    return render_template('admin/committee.html', members=members)

@admin_bp.route('/committee/add', methods=['POST'])
@login_required
def add_committee_member():
    members = load_committee()
    
    image_path = ""
    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename:
            image_path = save_uploaded_file(file, COMMITTEE_UPLOAD_FOLDER, prefix="member")
            
    new_member = {
        'id': 'mem' + str(uuid.uuid4())[:8],
        'name': request.form.get('name', '').strip(),
        'role': request.form.get('role', 'Member').strip(),
        'title': request.form.get('title', '').strip(),
        'email': request.form.get('email', '').strip(),
        'facebook': request.form.get('facebook', '').strip(),
        'image': image_path
    }
    members.append(new_member)
    save_committee(members)
    log_tracking("Digital", "Committee Member", f"Added committee member: {new_member['name']}")
    flash('Member added successfully.', 'success')
    return redirect(url_for('admin.committee'))

@admin_bp.route('/committee/edit/<member_id>', methods=['POST'])
@login_required
def edit_committee_member(member_id):
    members = load_committee()
    for mem in members:
        if mem['id'] == member_id:
            mem['name'] = request.form.get('name', mem.get('name', '')).strip()
            mem['role'] = request.form.get('role', mem.get('role', 'Member')).strip()
            mem['title'] = request.form.get('title', mem.get('title', '')).strip()
            mem['email'] = request.form.get('email', mem.get('email', '')).strip()
            mem['facebook'] = request.form.get('facebook', mem.get('facebook', '')).strip()
            
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename:
                    path = save_uploaded_file(file, COMMITTEE_UPLOAD_FOLDER, prefix="member")
                    if path: mem['image'] = path
            break
            
    save_committee(members)
    log_tracking("Digital", "Committee Member", "Updated a committee member")
    flash('Member updated.', 'success')
    return redirect(url_for('admin.committee'))

@admin_bp.route('/committee/delete/<member_id>', methods=['POST'])
@login_required
def delete_committee_member(member_id):
    members = [m for m in load_committee() if m['id'] != member_id]
    save_committee(members)
    log_tracking("Digital", "Committee Member", "Removed a committee member")
    flash('Member removed.', 'success')
    return redirect(url_for('admin.committee'))

# ── Tracking Matrix Management ─────────────────────────────────────────
@admin_bp.route('/tracking-matrix')
@login_required
def tracking_matrix():
    entries = load_tracking_matrix()
    return render_template('admin/tracking_matrix.html', entries=entries)

@admin_bp.route('/tracking-matrix/add', methods=['POST'])
@login_required
def add_tracking_matrix():
    entries = load_tracking_matrix()
    
    # Manual form date to friendly format
    try:
        from datetime import datetime
        dt = datetime.strptime(request.form.get('date', '').strip(), '%Y-%m-%d')
        date_str = dt.strftime('%B %d, %Y')
    except:
        date_str = request.form.get('date', '').strip()
        
    try:
        t_start = datetime.strptime(request.form.get('time_started', '').strip(), '%H:%M')
        h1 = t_start.strftime('%I').lstrip('0') or '12'
        start_str = f"{h1}:{t_start.strftime('%M %p')}"
    except:
        start_str = request.form.get('time_started', '').strip()
        
    try:
        t_end = datetime.strptime(request.form.get('time_completed', '').strip(), '%H:%M')
        h2 = t_end.strftime('%I').lstrip('0') or '12'
        end_str = f"{h2}:{t_end.strftime('%M %p')}"
    except:
        end_str = request.form.get('time_completed', '').strip()
        
    try:
        u_posted = datetime.strptime(request.form.get('updates_posted', '').strip(), '%Y-%m-%dT%H:%M')
        h3 = u_posted.strftime('%I').lstrip('0') or '12'
        posted_str = f"{u_posted.strftime('%B %d, %Y')}, {h3}:{u_posted.strftime('%M %p')}"
    except:
        posted_str = request.form.get('updates_posted', '').strip()

    new_entry = {
        'id': 'trk' + str(uuid.uuid4())[:8],
        'corner': request.form.get('corner', 'Physical').strip(),
        'date': date_str,
        'time_started': start_str,
        'time_completed': end_str,
        'type': request.form.get('type', 'Content').strip(),
        'description': request.form.get('description', '').strip(),
        'updates_posted': posted_str,
        'technical_officer': request.form.get('technical_officer', session.get('admin_user', 'System')).strip()
    }
    
    entries.insert(0, new_entry)
    save_tracking_matrix(entries)
    flash('Physical Corner entry added successfully.', 'success')
    return redirect(url_for('admin.tracking_matrix'))
