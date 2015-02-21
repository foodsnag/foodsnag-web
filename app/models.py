from datetime import datetime
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app, request, url_for
from flask.ext.login import UserMixin, AnonymousUserMixin
from . import db, login_manager


class Permission:
    ADMINISTER = 0x80

class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return self.name

attendees = db.Table('attendees',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('event_id', db.Integer, db.ForeignKey('event.id'))
)

class User(UserMixin, db.Model):
  __tablename__ = 'user'
  id = db.Column(db.Integer, primary_key=True)
  email = db.Column(db.String(64), unique=True, index=True)
  username = db.Column(db.String(64), unique=True, index=True)
  phone = db.Column(db.Integer, unique=True)
  text_updates = db.Column(db.Boolean)
  password_hash = db.Column(db.String(128))
  confirmed = db.Column(db.Boolean, default=False)
  member_since = db.Column(db.DateTime(), default=datetime.utcnow())
  location_id = db.Column(db.Integer, db.ForeignKey('location.id'))
  role_id = db.Column(db.Integer, db.ForeignKey('role.id'))

  def __init__(self, **kwargs):
    # Auto confirm for now
    self.confirmed = True

  @property
  def password(self):
    raise AttributeError('password is not a readable attribute')

  @password.setter
  def password(self, password):
    self.password_hash = generate_password_hash(password)

  def verify_password(self, password):
    return check_password_hash(self.password_hash, password)

  def can(self, permissions):
    return self.role is not None and \
        (self.role.permissions & permissions) == permissions

  def __repr__(self):
    return self.username

  # Flask-Login integration
  def is_authenticated(self):
    return True

  def is_active(self):
    return True

  def is_anonymous(self):
    return False

  def get_id(self):
    return self.id

  @staticmethod
  def make_admin(email):
    user = User.query.filter_by(email=email).first()
    user.role_id = Role.query.filter_by(name="Administrator").first().id
    db.session.commit()

@login_manager.user_loader
def load_user(user_id):
  return User.query.get(int(user_id))

class Event(db.Model):
  __tablename__ = 'event'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(128))
  serving = db.Column(db.String(128))
  place = db.Column(db.String(128))
  time = db.Column(db.DateTime, index=True)
  body = db.Column(db.Text)
  timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow())
  # Store the ids of the location of the event and the user who submitted id
  location_id = db.Column(db.Integer, db.ForeignKey('location.id'))
  author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
  attendees = db.relationship('User', secondary=attendees, backref=db.backref('events', lazy='dynamic'))

class Location(db.Model):
  __tablename__ = 'location'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(128))
  url = db.Column(db.String(128))
  # Store the users and events that belong to this location
  users = db.relationship('User', backref='location', lazy='dynamic')
  events = db.relationship('Event', backref='location', lazy='dynamic')

class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

    def is_authenticated(self):
        return False

login_manager.anonymous_user = AnonymousUser
