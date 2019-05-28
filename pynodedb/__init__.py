from flask import Flask, render_template, request
from flask_login import LoginManager
import sqlalchemy
import ipaddress

# import local modules
from . import functions as f
from .database import db, User, Node
from . import auth

login_manager = LoginManager()


def create_app(test_config=None):
    app = Flask(__name__)

    # Default Config
    app.config.from_mapping(
        DEBUG=True,
        SECRET_KEY='not very secure',
        SITENAME='pynodedb',
        DB_DRIVER=None,
        DB_HOST=None,
        DB_POST=None,
        DB_DATABASE=None,
        DB_USERNAME=None,
        DB_PASSWORD=None,
        SQLALCHEMY_TRACK_MODIFICATIONS=True,
        OAUTH_CLIENT_ID=None,
        OAUTH_CLIENT_SECRET=None,
        OAUTH_ACCESS_TOKEN_URL='https://members.air-stream.org/oauth/token',
        OAUTH_AUTHORIZE_URL='https://members.air-stream.org/oauth/authorize',
        OAUTH_API_BASE_URL='https://members.air-stream.org/api/',
        USE_SESSION_FOR_NEXT=True,
        GOOGLE_MAPS_API_KEY=None,
        MAP_DEFAULT_CENTRE=None,
    )

    # Load config file, if it exists
    app.config.from_pyfile('config.py', silent=True)

    # Jinja2 config
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True
    app.jinja_env.globals.update(random=f.random_string)

    # Custom Jinga2 filters
    @app.template_filter('ipv4address')
    def ipv4address(value):
        ipv4address = ipaddress.ip_address(value)
        return ipv4address

    @app.template_filter('ipv4network')
    def ipv4network(value):
        ipv4network = ipaddress.ip_network(value)
        return ipv4network

    # Initialise database
    app.config['SQLALCHEMY_DATABASE_URI'] = sqlalchemy.engine.url.URL(
        app.config['DB_DRIVER'],
        host=app.config['DB_HOST'],
        port=app.config['DB_POST'],
        database=app.config['DB_DATABASE'],
        username=app.config['DB_USERNAME'],
        password=app.config['DB_PASSWORD'],
    )
    with app.app_context():
        db.init_app(app)

    # Initilise Login Manager
    with app.app_context():
        login_manager.login_view = 'auth.login'
        login_manager.anonymous_user = auth.AnonymousUser

        login_manager.init_app(app)

    # Initilise  OAuth
    auth.oauth.register(
        'remote',
        client_id=app.config['OAUTH_CLIENT_ID'],
        client_secret=app.config['OAUTH_CLIENT_SECRET'],
        access_token_url=app.config['OAUTH_ACCESS_TOKEN_URL'],
        authorize_url=app.config['OAUTH_AUTHORIZE_URL'],
        api_base_url=app.config['OAUTH_API_BASE_URL'],
    )
    with app.app_context():
        auth.oauth.init_app(app)

    # Load user_id from session
    @login_manager.user_loader
    def load_user(user_id):
        user = User.get(user_id)
        return user

    # Register blueprints
    from . import nodes
    app.register_blueprint(nodes.bp)
    app.register_blueprint(auth.bp)
    from . import api
    app.register_blueprint(api.bp)

    @app.route('/')
    def home():
        return render_template('home.html')

    @app.route('/map')
    def map():
        return render_template('map.html')

    # Return app factory
    return app
