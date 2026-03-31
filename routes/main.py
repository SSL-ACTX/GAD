import os
import json
import math
from flask import Blueprint, render_template, request, jsonify, abort, current_app

main_bp = Blueprint('main', __name__)

# --- News Helper ---
POSTS_PER_PAGE = 6

def load_news():
    """Load all news items from data/news.json."""
    news_file = os.path.join(current_app.root_path, 'data', 'news.json')
    try:
        with open(news_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def load_carousel():
    """Load all image URLs from data/carousel.json."""
    carousel_file = os.path.join(current_app.root_path, 'data', 'carousel.json')
    try:
        with open(carousel_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def load_knowledge_products():
    """Load all knowledge products from data/knowledge_products.json."""
    knowledge_file = os.path.join(current_app.root_path, 'data', 'knowledge_products.json')
    try:
        with open(knowledge_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def load_brochures():
    """Load all brochures from data/brochures.json."""
    brochures_file = os.path.join(current_app.root_path, 'data', 'brochures.json')
    try:
        with open(brochures_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def load_livelihood_feeds():
    """Load all livelihood feeds from data/livelihood_feeds.json."""
    feeds_file = os.path.join(current_app.root_path, 'data', 'livelihood_feeds.json')
    try:
        with open(feeds_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def load_org_structure():
    """Load GFPS structure config."""
    org_file = os.path.join(current_app.root_path, 'data', 'org_structure.json')
    try:
        with open(org_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"chart_image": "", "pdf_url": "", "manual_url": ""}

def load_committee():
    """Load GFPS committee members."""
    committee_file = os.path.join(current_app.root_path, 'data', 'committee.json')
    try:
        with open(committee_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# --- Mock Database of Searchable Content ---
# This list is used by both the search results page and the live suggestion API.
searchable_content = [
    {'title': 'Annual GAD Plan and Budget', 'url': 'policies.reports', 'category': 'Reports'},
    {'title': 'GAD Focal Point System Structure', 'url': 'main.org_structure', 'category': 'About'},
    {'title': 'Gender Fair Language Circular', 'url': 'policies.policies_hub', 'category': 'Policies', 'cat_val': 'circulars'},
    {'title': 'Resolutions and Council Decrees', 'url': 'policies.policies_hub', 'category': 'Policies', 'cat_val': 'resolutions'},
    {'title': 'Memoranda and Internal Directives', 'url': 'policies.policies_hub', 'category': 'Policies', 'cat_val': 'memoranda'},
    {'title': 'Executive Orders and Designations', 'url': 'policies.policies_hub', 'category': 'Policies', 'cat_val': 'orders'},
    {'title': 'Buntis Congress 2024', 'url': 'projects.project_year', 'category': 'Projects', 'year': '2024'},
    {'title': 'Buntis Congress 2025', 'url': 'projects.project_year', 'category': 'Projects', 'year': '2025'},
    {'title': 'Vision and Mission Statement', 'url': 'main.vision_mission', 'category': 'About'},
    {'title': 'Contact the GAD Office', 'url': 'main.contact', 'category': 'About'},
    {'title': 'Latest News and Updates', 'url': 'main.news_hub', 'category': 'News'},
    {'title': 'GAD Committee Members', 'url': 'main.gad_committee', 'category': 'About'},
    {'title': 'Privacy Policy and Data Protection', 'url': 'legal.privacy_policy', 'category': 'Legal'},
    {'title': 'Terms of Use and Conditions', 'url': 'legal.terms_conditions', 'category': 'Legal'},
    {'title': 'System Developers Team', 'url': 'legal.developers', 'category': 'Team'},
    {'title': 'GAD Events Calendar', 'url': 'calendar.calendar_view', 'category': 'Calendar'},
    {'title': 'GAD Knowledge Products and IEC', 'url': 'main.knowledge_products', 'category': 'Resources'},
    {'title': 'Livelihood Program', 'url': 'main.livelihood_program', 'category': 'Resources'},
]

# --- Core Routes ---

@main_bp.route('/')
def index():
    news_items = load_news()
    latest_news = news_items[:3]  # Show 3 most recent on homepage
    carousel_images = load_carousel()
    return render_template('index.html', latest_news=latest_news, carousel_images=carousel_images)


@main_bp.route('/knowledge-products')
def knowledge_products():
    products = load_knowledge_products()
    return render_template('knowledge-products.html', products=products)


@main_bp.route('/brochures')
def brochures():
    brochures_list = load_brochures()
    return render_template('brochures.html', brochures=brochures_list)


@main_bp.route('/livelihood-program')
def livelihood_program():
    feeds = load_livelihood_feeds()
    return render_template('livelihood-program.html', feeds=feeds)

# --- About Section Routes ---

@main_bp.route('/about')
def about():
    return render_template('about/about.html')

@main_bp.route('/about/vision-mission')
def vision_mission():
    return render_template('about/vision-mission.html')

@main_bp.route('/about/org-structure')
def org_structure():
    data = load_org_structure()
    return render_template('about/org-structure.html', data=data)

@main_bp.route('/about/gad-committee')
def gad_committee():
    members = load_committee()
    return render_template('about/gad-committee.html', members=members)

@main_bp.route('/about/contact')
def contact():
    return render_template('about/contact.html')

# --- News Section Routes ---

@main_bp.route('/news')
def news_hub():
    news_items = load_news()
    page = request.args.get('page', 1, type=int)
    total_pages = max(1, math.ceil(len(news_items) / POSTS_PER_PAGE))
    page = max(1, min(page, total_pages))

    start = (page - 1) * POSTS_PER_PAGE
    end = start + POSTS_PER_PAGE
    paginated = news_items[start:end]

    return render_template(
        'news/news.html',
        news_items=paginated,
        page=page,
        total_pages=total_pages,
    )

@main_bp.route('/news/<news_id>')
def news_detail(news_id):
    news_items = load_news()
    article = next((item for item in news_items if item.get('id') == news_id), None)
    if article is None:
        abort(404)
    return render_template('news/news-detail.html', article=article)

# --- Search Functionality ---

@main_bp.route('/search')
def search():
    """Renders the full search results page."""
    query = request.args.get('q', '').strip()
    results = []
    if query:
        # Search through our content list (Case-insensitive)
        results = [item for item in searchable_content if query.lower() in item['title'].lower()]
    return render_template('search_results.html', query=query, results=results)

@main_bp.route('/api/suggestions')
def get_suggestions():
    """Returns a JSON list of matches for the live 'ghost' dropdown."""
    query = request.args.get('q', '').strip().lower()
    
    # Only start searching after 2 characters to save server resources
    if not query or len(query) < 2:
        return jsonify([])
    
    # Find matching titles
    matches = [item['title'] for item in searchable_content if query in item['title'].lower()]
    
    # Return top 5 matches to keep the dropdown clean
    return jsonify(matches[:5])