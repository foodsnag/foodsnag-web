import sched, time, datetime
from flask import Flask, abort, redirect, url_for
from flask.ext.bootstrap import Bootstrap
from .extensions import db, celery, login_manager
from flask.ext.admin import Admin, BaseView, expose, AdminIndexView
from flask.ext.admin.contrib.sqla import ModelView
from wtforms.fields import SelectField, PasswordField
from config import config
from celery.task import periodic_task
from datetime import timedelta
from .models import Permission, User, Event, Location
from .tasks import upcoming_notify

bootstrap = Bootstrap()

def create_app(config_name):
  app = Flask(__name__)
  app.config.from_object(config[config_name])
  config[config_name].init_app(app)
  
  admin.init_app(app)

  bootstrap.init_app(app)
  db.init_app(app)
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

# Flask-Admin Views

class HomeView(AdminIndexView):
    @expose('/')
    def index(self):
        print(current_user.is_authenticated())
        if not current_user.is_authenticated():
            return redirect(url_for('auth.login'))
        return super(HomeView, self).index()

admin = Admin(index_view=HomeView())


# Setup More Admin view stuff

class UserView(ModelView):
    column_list = ('username', 'email', 'member_since', 'role', 'location')
    form_excluded_columns = ('password_hash','avatar_hash')
    column_searchable_list = ('username', 'email')

    def __init__(self, session):
        # You can pass name and other parameters if you want to
        super(UserView, self).__init__(User, session, name="Users")


    def is_accessible(self):
        if current_user.can(Permission.ADMINISTER):
            return True

    def is_visible(self):
        if current_user.can(Permission.ADMINISTER):
            return True

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(url_for('auth.login'))

class EventView(ModelView):

    column_list = ( 'id', 'name', 'place', 'time', 'location', 'author'  )
    column_searchable_list = ( 'name', 'place' )

    def __init__(self, session):
        # You can pass name and other parameters if you want to
        super(EventView, self).__init__(Event, session, name="Events")

    def is_accessible(self):
        if current_user.can(Permission.ADMINISTER):
            return True

    def is_visible(self):
        if current_user.can(Permission.ADMINISTER):
            return True

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(url_for('auth.login'))

class LocationView(ModelView):
    
    column_list = ( 'id', 'name', 'url' )
    column_searchable_list = ( 'name', )

    def __init__(self, session):
        # You can pass name and other parameters if you want to
        super(LocationView, self).__init__(Location, session, name="Locations")


    def is_accessible(self):
        if current_user.can(Permission.ADMINISTER):
            return True

    def is_visible(self):
        if current_user.can(Permission.ADMINISTER):
            return True

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(url_for('auth.login'))

admin.add_view(UserView(db.session))
admin.add_view(EventView(db.session))
admin.add_view(LocationView(db.session))
