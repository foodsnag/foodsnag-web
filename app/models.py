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
  submitted = db.relationship('Event', backref='author', lazy='dynamic')
  role_id = db.Column(db.Integer, db.ForeignKey('role.id'))

  def __init__(self, **kwargs):
    # Auto confirm for now
    self.confirmed = True

  def is_attending(self, eventId):
    e = Event.query.get(eventId)
    if self in e.attendees:
      return True
    else:
      return False

  @property
  def password(self):
    raise AttributeError('password is not a readable attribute')

  @password.setter
  def password(self, password):
    self.password_hash = generate_password_hash(password)

  @staticmethod
  def generate_fake(count=10):
    from sqlalchemy.exc import IntegrityError
    from random import seed
    import random
    import forgery_py

    seed()
    for i in range(count):
      u = User()
      u.email=forgery_py.internet.email_address()
      u.username=forgery_py.internet.user_name(True)
      u.password=forgery_py.lorem_ipsum.word()
      u.confirmed=True
      u.location_id=Location.query.get(random.randrange(1, Location.query.count())).id
      u.member_since=forgery_py.date.date(True)

      db.session.add(u)
      try:
        db.session.commit()
      except IntegrityError:
        db.session.rollback()

  def verify_password(self, password):
    return check_password_hash(self.password_hash, password)

  def can(self, permissions):
    return self.role is not None and \
        (self.role.permissions & permissions) == permissions

  def __repr__(self):
    return self.username

  def __hash__(self):
    return id(self)

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

  def to_json(self):
    json_post = {
      'id' : self.id,
      'email' : self.email,
      'member_since' : self.member_since,
      'location_id' : self.location_id
    }
    return json_post

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

  def __hash__(self):
    return id(self)

  def generate_fake(count=100):
    from sqlalchemy.exc import IntegrityError
    from random import seed
    import random
    import forgery_py

    seed()
    for i in range(count):
      e = Event()
      e.name=forgery_py.lorem_ipsum.word()
      e.serving=forgery_py.lorem_ipsum.word()
      e.place=forgery_py.lorem_ipsum.word()
      e.time=forgery_py.date.date(True)
      e.body=forgery_py.lorem_ipsum.sentence()
      e.author_id=User.query.get(random.randrange(1, User.query.count())).id
      e.location_id=Location.query.get(random.randrange(1, Location.query.count())).id

      db.session.add(e)
      try:
        db.session.commit()
      except IntegrityError:
        db.session.rollback()

  def __repr__(self):
    return self.name

  def attend_event(self, user_id):
    u = User.query.get(user_id)
    self.attendees.append(u)

    db.session.add(self)
    db.session.commit()

  def unattend_event(self, user_id):
    self.attendees.remove(User.query.get(user_id))
    db.session.commit()

  def to_json(self):
    json_post = {
      'id' : self.id,
      'author_id' : self.author_id,
      'location_id' : self.location_id,
      'name' : self.name,
      'place' : self.place,
      'serving' : self.serving,
      'time' : self.time,
      'timestamp' : self.timestamp,
      'body' : self.body
    }
    return json_post

  def __hash__(self):
    return id(self)


class Location(db.Model):
  __tablename__ = 'location'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(128))
  url = db.Column(db.String(128))
  # Store the users and events that belong to this location
  users = db.relationship('User', backref='location', lazy='dynamic')
  events = db.relationship('Event', backref='location', lazy='dynamic')

  def __repr__(self):
    return self.name

  def to_json(self):
    json_post = {
      'id' : self.id,
      'name' : self.name
    }
    return json_post

  def __hash__(self):
    return id(self)

class AnonymousUser(AnonymousUserMixin):
  def can(self, permissions):
      return False

  def is_administrator(self):
      return False

  def is_authenticated(self):
      return False


login_manager.anonymous_user = AnonymousUser
