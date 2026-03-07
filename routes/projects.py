import os
import json
from flask import Blueprint, render_template

projects_bp = Blueprint('projects', __name__)

PROJECTS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'projects.json')

def load_projects():
    try:
        with open(PROJECTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

@projects_bp.route('/projects')
def projects_hub():
    return render_template('projects/projects.html')

@projects_bp.route('/projects/year/<year>')
def project_year(year):
    all_projects = load_projects()
    projects = [p for p in all_projects if p.get('year') == year]
    return render_template('projects/project-year.html', year=year, projects=projects)

@projects_bp.route('/projects/archive')
def projects_archive():
    all_projects = load_projects()
    years = sorted(set(p.get('year') for p in all_projects), reverse=True)
    return render_template('projects/archive.html', years=years)