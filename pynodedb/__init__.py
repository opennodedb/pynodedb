from flask import Flask
import sqlalchemy
import pynodedb.database as database
import ipaddress


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
    )

    # Load config file, if it exists
    app.config.from_pyfile('config.py', silent=True)

    # Jinja2 config
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True

    # Custom Jinga2 filters
    @app.template_filter('ipv4address')
    def ipv4address(value):
        ipv4address = ipaddress.ip_address(value)
        return ipv4address

    @app.template_filter('ipv4network')
    def ipv4network(value):
        ipv4network = ipaddress.ip_network(value)
        return ipv4network

    # nodes Routes
    from . import nodes
    app.register_blueprint(nodes.bp)

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
        database.db.init_app(app)

    # Return app factory
    return app
