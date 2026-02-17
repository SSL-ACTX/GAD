from flask import Blueprint, render_template

projects_bp = Blueprint('projects', __name__)

@projects_bp.route('/projects')
def projects_hub():
    return render_template('projects/projects.html')

@projects_bp.route('/projects/year/<year>')
def project_year(year):
    return render_template('projects/project-year.html', year=year)

@projects_bp.route('/projects/archive')
def projects_archive():
    return render_template('projects/archive.html')