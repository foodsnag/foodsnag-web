import sched, time, datetime
from flask import Flask, abort, redirect, url_for
from .extensions import db, celery, login_manager, HomeView, UserView, EventView, LocationView
from flask.ext.admin import Admin, BaseView, expose, AdminIndexView
from flask.ext.admin.contrib.sqla import ModelView
from wtforms.fields import SelectField, PasswordField
from config import config
from celery.task import periodic_task
from datetime import timedelta
from .models import Permission, User, Event, Location
from .tasks import upcoming_notify


def create_app(config_name):
  app = Flask(__name__)
  app.config.from_object(config[config_name])
  config[config_name].init_app(app)
  
  db.init_app(app)

  admin = Admin(index_view=HomeView())

  admin.init_app(app)
  celery.init_app(app)
  celery.conf.CELERY_TIMEZONE = 'America/New_York'


  login_manager.session_protection = 'strong'
  login_manager.login_view = 'auth.login'
  login_manager.init_app(app)

  from .main import main as main_blueprint
  app.register_blueprint(main_blueprint)

  from .auth import auth as auth_blueprint
  app.register_blueprint(auth_blueprint, url_prefix='/auth')

  from .api import api as api_blueprint
  app.register_blueprint(api_blueprint, url_prefix='/api')

  return app


