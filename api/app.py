from flask import Flask
from sqlalchemy_utils.functions import database_exists
from flask_restful import Api
import logging
from database import db
from config import config
from models import Center, Animal, Specie, Authenticator


# Create app
app = Flask(config["GENERAL"]["APP_NAME"])
# Configure logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

logging.basicConfig(format="%(name)s | %(levelname)s | %(asctime)s | %(message)s",
                    filename=config["LOGGING"]["LOG_PATH"],
                    level=int(config["LOGGING"]["LOG_LEVEL"]))


# Configure app
app.config["SQLALCHEMY_DATABASE_URI"] = config["DATABASE"]["SQLALCHEMY_DATABASE_URI"]
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = config["DATABASE"]["SQLALCHEMY_TRACK_MODIFICATIONS"]
app.config["SECRET_KEY"] = config["GENERAL"]["SECRET_KEY"]
app.config['PROPAGATE_EXCEPTIONS'] = True

# Init and optionally create database
with Flask.app_context(app):
    try:
        db.init_app(app)
        if not database_exists(app.config["SQLALCHEMY_DATABASE_URI"]):
            db.create_all()
            app.logger.info("Creating database at " +
                            app.config["SQLALCHEMY_DATABASE_URI"])
        else:
            app.logger.info("Using database at " +
                            app.config["SQLALCHEMY_DATABASE_URI"])
    except Exception:
        app.logger.exception(
            "Could not create/open database file, check config.ini")
        exit(1)

# Create API
api = Api(app)
