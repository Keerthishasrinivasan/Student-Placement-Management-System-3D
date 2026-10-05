import os
from flask import Flask, render_template, session
from config import config_by_name
from models import db, User

def create_app(config_name='default'):
    """Application factory for Student Placement Management System."""
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # Initialize extensions
    db.init_app(app)

    # Register blueprints
    from routes.main import main_bp
    from routes.auth import auth_bp
    from routes.student import student_bp
    from routes.recruiter import recruiter_bp
    from routes.admin import admin_bp
    from routes.api import api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(recruiter_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)

    # Context processor to inject user information into templates
    @app.context_processor
    def inject_user():
        current_user = None
        if 'user_id' in session:
            current_user = User.query.get(session['user_id'])
        return dict(current_user=current_user)

    # Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('base.html', not_found=True), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('base.html', server_error=True), 500

    # Ensure tables exist on start
    with app.app_context():
        db.create_all()

    return app

app = create_app(os.environ.get('FLASK_ENV', 'default'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
