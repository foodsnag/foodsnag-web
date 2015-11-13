from datetime import datetime, timedelta, time
from dateutil import tz
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app, request, url_for
from flask.ext.login import UserMixin, AnonymousUserMixin
from .extensions import db, login_manager
#from .tasks import event_notify

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
  email_notifications = db.Column(db.Boolean)
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
  def generate_fake(count=10, loc=None):
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
      if loc == None:
        u.location_id=Location.query.get(random.randrange(1, Location.query.count())).id
      else:
        u.location_id=loc
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

  def num_submitted(self):
    return self.submitted.count()

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
  name = db.Column(db.String(128), index=True)
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

  def generate_fake(count=100,loc=None):
    from sqlalchemy.exc import IntegrityError
    from random import seed
    import random
    import forgery_py

    rand_name = ["Party!", "Study Session", "Gosnell Open House", "Student Gov Event"]
    rand_locs = ["GOS 3365", "CAR 1250", "BRN 352", "ORN 107", "GOL 3200", "EAS 1243", "Library Lobby", "Infinity Quad", "Field House"]
    rand_serv = ["Pizza", "Pizza", "Pizza and snacks", "Snacks", "BBQ", "Hamburgers and Hotdogs"]
    seed()
    for i in range(count):
      e = Event()
      #e.name=forgery_py.lorem_ipsum.word()
      #e.serving=forgery_py.lorem_ipsum.word()
      #e.place=forgery_py.lorem_ipsum.word()
      e.name = rand_name[random.randint(0,len(rand_name)-1)]
      e.serving = rand_serv[random.randint(0,len(rand_serv)-1)]
      e.place = rand_locs[random.randint(0,len(rand_locs)-1)]
      e.time= datetime.combine(forgery_py.date.date(past=False), time(hour=random.randrange(0,23),minute=random.randrange(0,59)))
      e.body=forgery_py.lorem_ipsum.sentence()
      e.author_id=User.query.get(random.randrange(1, User.query.count())).id
      if loc == None:
        e.location_id=Location.query.get(random.randrange(1, Location.query.count())).id
      else:
        e.location_id=loc
      db.session.add(e)

      if not i % 100:
        print(i)
    try:
      db.session.commit()
    except IntegrityError:
      db.session.rollback()

  def future_events(location_id):
    """ Returns all future events """
    # Autodetects timezone and lists events in the future
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()
    utc = datetime.utcnow()
    utc = utc.replace(tzinfo=from_zone)
    actual = utc.astimezone(to_zone)
    all_events = Event.query.filter_by(location_id=location_id)

    return all_events.filter(Event.time>actual).all()

  def __repr__(self):
    return self.name

  def attend_event(self, user_id):
    """ Adds a user to an event's attendees """
    u = User.query.get(user_id)
    self.attendees.append(u)
    # Create a notification event
    # TODO: check if user wants notifications
    # Have to make local to utc
    to_zone = tz.tzutc()
    from_zone = tz.tzlocal()
    utc = self.time
    utc = utc.replace(tzinfo=from_zone)
    alarm = utc.astimezone(to_zone)

    # Notify 30 min before event

    alarm = alarm - timedelta(minutes=30)
    #event_notify.apply_async( (u.username, alarm), eta=alarm )

    db.session.add(self)
    db.session.commit()

  def unattend_event(self, user_id):
    """ Removes a user from an event's attendees """
    self.attendees.remove(User.query.get(user_id))
    db.session.commit()

  def num_attendees(self):
    """ Returns the number of attendees going to an event """
    num = len(self.attendees)
    return num

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
  name = db.Column(db.String(128), index=True)
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

  def num_events(self):
    return self.events.count()

  def num_users(self):
    return self.users.count()

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
