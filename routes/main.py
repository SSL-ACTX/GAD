from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

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

@main_bp.route('/news')
def news_hub():
    return render_template('news/news.html')

@main_bp.route('/news/article-1')
def news_detail():
    return render_template('news/news-detail.html')