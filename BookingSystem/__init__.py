import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from datetime import timedelta
from flask_cors import CORS
from flask_migrate import Migrate
from flask import Blueprint

main = Blueprint('main', __name__, template_folder='templates')

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
mail = Mail()
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = '2770d4fd598f5a792ebce414a891f412'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:12345@localhost:5433/postgres'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'kf515335@gmail.com'  # Replace with env variable
    app.config['MAIL_PASSWORD'] = 'rsjptgkiwfqrxtwx'    # Replace with env variable
    app.config['MAIL_DEFAULT_SENDER'] = 'kf515335@gmail.com'
    app.config['SESSION_PERMANENT'] = True
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_PROTECTION'] = 'strong'
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
    app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # Limit file size to 2MB
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static/profile_pics')


    # Ensure the upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    CORS(app)
    db.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)



    login_manager.login_view = 'main.traveler_login'
    login_manager.login_message_category = 'info'

    # Import and register blueprints
    from BookingSystem.routes import main
    from BookingSystem.Admin_Page import admin
    from BookingSystem.TourOperator_Page import touroperator
    from BookingSystem.TourGuide_Page import tourguide

    app.register_blueprint(main)
    app.register_blueprint(admin, url_prefix='/admin')
    app.register_blueprint(touroperator, url_prefix='/touroperator')
    app.register_blueprint(tourguide, url_prefix='/tourguide')

    with app.app_context():
        db.create_all()

    return app
