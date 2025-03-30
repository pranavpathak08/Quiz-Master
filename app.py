from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from werkzeug.security import generate_password_hash
from models.models import db, User # Import models correctly

app = Flask(__name__)

app.config['SECRET_KEY'] = "ade26f904f1afa3c56fafadc438b8239"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quizmasterdb.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)  # Initialize database with app

# Import routes after initializing the app
from controllers.routes import routes_blueprint
from controllers.auth_routes import auth_blueprint
from controllers.admin_routes import admin_blueprint
from controllers.user_routes import user_blueprint

# Register Blueprints
app.register_blueprint(routes_blueprint)
app.register_blueprint(auth_blueprint, url_prefix="/auth")
app.register_blueprint(admin_blueprint, url_prefix="/admin")
app.register_blueprint(user_blueprint, url_prefix="/user")

@app.context_processor
def inject_user():
    return dict(current_user=current_user)

# Login Manager
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  

        # Create default admin if not exists
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@example.com',
                password=generate_password_hash('admin123', method='pbkdf2:sha256'),
                full_name='Administrator',
                qualification='Admin',
                dob='N/A',
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
            print("Admin account created: Username - admin, Password - admin123 (hashed)")

    app.run(debug=True)
