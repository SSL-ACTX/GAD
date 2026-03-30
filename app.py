import os
import json
import subprocess
from datetime import datetime
from flask import Flask, render_template, request, abort
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler

# Import Blueprints
from routes.main import main_bp
from routes.policies import policies_bp
from routes.projects import projects_bp
from routes.legal import legal_bp
from routes.auth import auth_bp
from routes.calendar import calendar_bp
from routes.admin import admin_bp

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Basic Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-placeholder-123')

# ---------------------------------------------------------
# 1. PRODUCTION SECURITY HEADERS (Flask-Talisman)
# ---------------------------------------------------------
# Content Security Policy (CSP) - Tells the browser which sources to trust
csp = {
    'default-src': '\'self\'',
    'script-src': [
        '\'self\'',
        'https://cdn.tailwindcss.com',
        'https://cdnjs.cloudflare.com',
        'https://connect.facebook.net',
        '\'unsafe-inline\''  # Necessary for Tailwind CDN and inline scripts
    ],
    'style-src': [
        '\'self\'',
        'https://fonts.googleapis.com',
        'https://cdnjs.cloudflare.com',
        '\'unsafe-inline\''  # Necessary for Tailwind and your custom aurora-glow styles
    ],
    'font-src': [
        '\'self\'',
        'https://fonts.gstatic.com',
        'https://cdnjs.cloudflare.com'
    ],
    'img-src': [
        '\'self\'',
        'data:',
        'https://images.unsplash.com',
        'https://ui-avatars.com',
        'https://wsrv.nl',
        'https://i.ibb.co'
    ],
    'frame-src': [
        '\'self\'',
        'https://www.facebook.com',
        'https://web.facebook.com'
    ]
}

# Talisman enforces HTTPS and sets security headers (XSS, Clickjacking protection)
talisman = Talisman(app, content_security_policy=csp, force_https=False)

# ---------------------------------------------------------
# 2. ANTI-SCRAPER RATE LIMITING (Flask-Limiter)
# ---------------------------------------------------------

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)

# ---------------------------------------------------------
# 3. MANUAL BOT / SCRAPER FILTERING
# ---------------------------------------------------------
@app.before_request
def block_bots():
    user_agent = request.headers.get('User-Agent', '').lower()
    # List of common scraper/automation signatures
    bot_keywords = [
        'python-requests', 'curl', 'wget', 'selenium', 
        'headless', 'scrapy', 'bot', 'spider', 'ltx71'
    ]
    if any(keyword in user_agent for keyword in bot_keywords):
        # Abort with a 403 Forbidden error
        return abort(403)

# ---------------------------------------------------------
# 4. BLUEPRINT REGISTRATION
# ---------------------------------------------------------
app.register_blueprint(main_bp)
app.register_blueprint(policies_bp)
app.register_blueprint(projects_bp)
app.register_blueprint(legal_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(calendar_bp)
app.register_blueprint(admin_bp)

# ---------------------------------------------------------
# 5. GLOBAL CONTEXT PROCESSOR
# ---------------------------------------------------------
SITE_CONFIG_FILE = os.path.join(app.root_path, 'data', 'site_config.json')


def load_site_config():
    """Load site-wide configuration used by templates and admin settings."""
    default = {
        'policies': {'start_year': 2002, 'current_year': datetime.now().year},
        'reports': {'years': ['2024', '2023', '2022', '2021', '2020']}
    }

    try:
        with open(SITE_CONFIG_FILE, 'r', encoding='utf-8') as f:
            raw = json.load(f)
            if not isinstance(raw, dict):
                return default
            # Merge defaults without overwriting existing values
            merged = default.copy()
            merged.update(raw)
            # Ensure nested keys exist
            merged['policies'] = {**default['policies'], **(raw.get('policies') or {})}
            merged['reports'] = {**default['reports'], **(raw.get('reports') or {})}
            return merged
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def save_site_config(config: dict):
    """Persist the site configuration to disk."""
    os.makedirs(os.path.dirname(SITE_CONFIG_FILE), exist_ok=True)
    with open(SITE_CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


@app.context_processor
def inject_global_data():
    """Inject navigation, site config, and smart breadcrumbs into every template."""
    import json
    
    # 1. Project Years
    projects_file = os.path.join(app.root_path, 'data', 'projects.json')
    try:
        with open(projects_file, 'r', encoding='utf-8') as f:
            projects = json.load(f)
        years = sorted(set(p.get('year', '') for p in projects if p.get('year')), reverse=True)
    except (FileNotFoundError, json.JSONDecodeError):
        years = []

    # 2. Site Config
    site_config = load_site_config()

    return dict(
        nav_project_years=years,
        site_config=site_config,
        now=datetime.now()
    )


# ---------------------------------------------------------
# 5. GLOBAL ERROR HANDLERS
# ---------------------------------------------------------
@app.errorhandler(404)
def page_not_found(e):
    # Returns landing page with 404 status
    return render_template('index.html'), 404

@app.errorhandler(403)
def forbidden(e):
    return "Access Denied: Automated scraping or unauthorized access is prohibited.", 403

@app.errorhandler(429)
def ratelimit_handler(e):
    return "Too many requests. Please try again later.", 429

# ---------------------------------------------------------
# 6. SCHEDULER IMPLEMENTATION
# ---------------------------------------------------------
def run_news_scraper():
    """Background job to run the scraper."""
    script_path = os.path.join(app.root_path, 'scripts', 'scrape_news.py')
    print(f"[{os.getpid()}] Running scheduled news scraper...")
    try:
        subprocess.run(['python', script_path], check=True)
        print("Scheduled scraper finished successfully.")
    except Exception as e:
        print(f"Scheduled scraper failed: {e}")

# Try to initialize the scheduler
scheduler = BackgroundScheduler()

SCHEDULE_FILE = os.path.join(app.root_path, 'data', 'scraper_schedule.json')

def load_schedule():
    try:
        if os.path.exists(SCHEDULE_FILE):
            with open(SCHEDULE_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading schedule: {e}")
    return {"enabled": False, "hour": "2", "minute": "0"}

def setup_scheduler():
    config = load_schedule()
    # Remove existing job if any
    try:
        scheduler.remove_job('news_scraper_job')
    except:
        pass
        
    if config.get('enabled', False):
        hour = config.get('hour', '2')
        minute = config.get('minute', '0')
        scheduler.add_job(
            id='news_scraper_job',
            func=run_news_scraper,
            trigger='cron',
            hour=hour,
            minute=minute,
            replace_existing=True
        )
        print(f"Scraper scheduled for {hour}:{minute} daily.")
    else:
        print("Scraper schedule is disabled.")

# Don't start scheduler in Werkzeug reloader process to avoid duplicate jobs
if os.environ.get('WERKZEUG_RUN_MAIN') == 'true' or not app.debug:
    setup_scheduler()
    scheduler.start()

# ---------------------------------------------------------
# 7. EXECUTION
# ---------------------------------------------------------
if __name__ == '__main__':
    # Set DEBUG=False in your .env file for production
    debug_mode = os.getenv('DEBUG', 'True') == 'True'
    app.run(debug=debug_mode)