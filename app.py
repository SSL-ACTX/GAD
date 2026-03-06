import os
from flask import Flask, render_template, request, abort
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from dotenv import load_dotenv

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
        'https://ui-avatars.com'
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
# 6. EXECUTION
# ---------------------------------------------------------
if __name__ == '__main__':
    # Set DEBUG=False in your .env file for production
    debug_mode = os.getenv('DEBUG', 'True') == 'True'
    app.run(debug=debug_mode)