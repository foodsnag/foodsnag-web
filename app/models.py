from datetime import datetime
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app, request, url_for
from flask.ext.login import UserMixin
from . import db, login_manager


class User(UserMixin, db.Model):
  __tablename__ = 'users'
  id = db.Column(db.Integer, primary_key=True)
  email = db.Column(db.String(64), unique=True, index=True)
  username = db.Column(db.String(64), unique=True, index=True)
  phone = db.Column(db.Integer, unique=True)
  text_updates = db.Column(db.Boolean)
  password_hash = db.Column(db.String(128))
  confirmed = db.Column(db.Boolean, default=False)
  member_since = db.Column(db.DateTime(), default=datetime.utcnow())
  events = db.relationship('Event', backref='author', lazy='dynamic')
  location_id = db.Column(db.Integer, db.ForeignKey('locations.id'))

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

@login_manager.user_loader
def load_user(user_id):
  return User.query.get(int(user_id))

class Event(db.Model):
  __tablename__ = 'events'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(128))
  serving = db.Column(db.String(128))
  place = db.Column(db.String(128))
  time = db.Column(db.DateTime, index=True)
  body = db.Column(db.Text)
  timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow())
  # Store the ids of the location of the event and the user who submitted id
  location_id = db.Column(db.Integer, db.ForeignKey('locations.id'))
  author_id = db.Column(db.Integer, db.ForeignKey('users.id'))

class Location(db.Model):
  __tablename__ = 'locations'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(128))
  url = db.Column(db.String(128))
  # Store the users and events that belong to this location
  users = db.relationship('User', backref='location', lazy='dynamic')
  events = db.relationship('Event', backref='location', lazy='dynamic')

