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
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'pdf', 'docx', 'doc', 'mp4', 'webm', 'ogg'}
POLICIES_UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads', 'policies')
PROJECTS_UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads', 'projects')
KNOWLEDGE_UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads', 'knowledge')
BROCHURES_UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads', 'brochures')

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
    flash('Knowledge Product updated.', 'success')
    return redirect(url_for('admin.knowledge'))

@admin_bp.route('/knowledge/delete/<item_id>', methods=['POST'])
@login_required
def delete_knowledge_entry(item_id):
    all_items = [i for i in load_knowledge_products() if i['id'] != item_id]
    save_knowledge_products(all_items)
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
    flash('Brochure updated.', 'success')
    return redirect(url_for('admin.brochures'))

@admin_bp.route('/brochures/delete/<item_id>', methods=['POST'])
@login_required
def delete_brochure(item_id):
    items = [i for i in load_brochures() if i['id'] != item_id]
    save_brochures(items)
    flash('Brochure deleted.', 'success')
    return redirect(url_for('admin.brochures'))
