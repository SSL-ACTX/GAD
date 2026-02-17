from flask import Blueprint, render_template, request, jsonify

main_bp = Blueprint('main', __name__)

# --- Mock Database of Searchable Content ---
# This list is used by both the search results page and the live suggestion API.
searchable_content = [
    {'title': 'Annual GAD Plan and Budget', 'url': 'policies.reports', 'category': 'Reports'},
    {'title': 'GAD Focal Point System Structure', 'url': 'main.org_structure', 'category': 'About'},
    {'title': 'Gender Fair Language Circular', 'url': 'policies.policies_hub', 'category': 'Policies', 'cat_val': 'circulars'},
    {'title': 'Resolutions and Council Decrees', 'url': 'policies.policies_hub', 'category': 'Policies', 'cat_val': 'resolutions'},
    {'title': 'Memoranda and Internal Directives', 'url': 'policies.policies_hub', 'category': 'Policies', 'cat_val': 'memoranda'},
    {'title': 'Office Orders and Designations', 'url': 'policies.policies_hub', 'category': 'Policies', 'cat_val': 'orders'},
    {'title': 'Buntis Congress 2024', 'url': 'projects.project_year', 'category': 'Projects', 'year': '2024'},
    {'title': 'Buntis Congress 2025', 'url': 'projects.project_year', 'category': 'Projects', 'year': '2025'},
    {'title': 'Vision and Mission Statement', 'url': 'main.vision_mission', 'category': 'About'},
    {'title': 'Contact the GAD Office', 'url': 'main.contact', 'category': 'About'},
    {'title': 'Latest News and Updates', 'url': 'main.news_hub', 'category': 'News'},
    {'title': 'GAD Committee Members', 'url': 'main.gad_committee', 'category': 'About'},
    {'title': 'Privacy Policy and Data Protection', 'url': 'legal.privacy_policy', 'category': 'Legal'},
    {'title': 'Terms of Use and Conditions', 'url': 'legal.terms_conditions', 'category': 'Legal'},
    {'title': 'System Developers Team', 'url': 'legal.developers', 'category': 'Team'},
]

# --- Core Routes ---

@main_bp.route('/')
def index():
    return render_template('index.html')

# --- About Section Routes ---

@main_bp.route('/about')
def about():
    return render_template('about/about.html')

@main_bp.route('/about/vision-mission')
def vision_mission():
    return render_template('about/vision-mission.html')

@main_bp.route('/about/org-structure')
def org_structure():
    return render_template('about/org-structure.html')

@main_bp.route('/about/gad-committee')
def gad_committee():
    return render_template('about/gad-committee.html')

@main_bp.route('/about/contact')
def contact():
    return render_template('about/contact.html')

# --- News Section Routes ---

@main_bp.route('/news')
def news_hub():
    return render_template('news/news.html')

@main_bp.route('/news/article-1')
def news_detail():
    return render_template('news/news-detail.html')

# --- Search Functionality ---

@main_bp.route('/search')
def search():
    """Renders the full search results page."""
    query = request.args.get('q', '').strip()
    results = []
    if query:
        # Search through our content list (Case-insensitive)
        results = [item for item in searchable_content if query.lower() in item['title'].lower()]
    return render_template('search-results.html', query=query, results=results)

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