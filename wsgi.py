from app import create_app
from seeds import seed_database
import os

app = create_app(os.environ.get('FLASK_ENV', 'production'))

# Automatically seed if database is new
with app.app_context():
    from models import User
    try:
        if not User.query.first():
            print("Auto-seeding initial placement dataset...")
            seed_database()
    except Exception as e:
        print("Database auto-seed check:", e)

if __name__ == "__main__":
    app.run()
