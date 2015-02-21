#!/usr/bin/env python
import os, csv
from app import create_app, db
from app.models import User, Location
from flask.ext.script import Manager, Shell

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)


def make_shell_context():
    return dict(app=app, db=db, User=User)
manager.add_command("shell", Shell(make_context=make_shell_context))

@manager.command
def mkdb():
  db.create_all()

@manager.command
def adduser(email, username, password):
  """Register a new user."""
  user = User(email=email, username=username, password=password)
  db.session.add(user)
  db.session.commit()

@manager.command
def importschools(fpath):
  n = 0

  with open(fpath) as f:
    reader = csv.reader(f)
    for row in reader:
      name = row[1].replace('&amp','&')
      if(not Location.query.filter_by(name=name).first()):
        school = Location(name=name, url=row[2])
        db.session.add(school)
        n += 1

  print('%d new locations added to database' % n)
  db.session.commit()

@manager.command
def test():
  """Run the unit tests."""
  import unittest
  tests = unittest.TestLoader().discover('tests')
  unittest.TextTestRunner(verbosity=2).run(tests)


if __name__ == '__main__':
    manager.run()
