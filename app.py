from flask import Flask, render_template
from routes.main import main_bp
from routes.policies import policies_bp
from routes.projects import projects_bp
from routes.legal import legal_bp
from routes.auth import auth_bp

app = Flask(__name__)

# Register Blueprints
app.register_blueprint(main_bp)
app.register_blueprint(policies_bp)
app.register_blueprint(projects_bp)
app.register_blueprint(legal_bp)
app.register_blueprint(auth_bp)

# Global Error Handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('index.html'), 404

if __name__ == '__main__':
    app.run(debug=True)