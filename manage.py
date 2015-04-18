#!/usr/bin/env python
import os, csv
COV = None
if os.environ.get('FLASK_COVERAGE'):
    import coverage
    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()

if os.path.exists('.env'):
    print('Importing environment from .env...')
    for line in open('.env'):
        var = line.strip().split('=')
        if len(var) == 2:
            os.environ[var[0]] = var[1]

from app import create_app, db
from app.models import User, Location, Role, Event
from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db)

manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def test(coverage=False):
    """Run the unit tests."""
    if coverage and not os.environ.get('FLASK_COVERAGE'):
        import sys
        os.environ['FLASK_COVERAGE'] = '1'
        os.execvp(sys.executable, [sys.executable] + sys.argv)
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
    if COV:
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'tmp/coverage')
        COV.html_report(directory=covdir)
        print('HTML version: file://%s/index.html' % covdir)
        COV.erase()


@manager.command
def profile(length=25, profile_dir=None):
    """Start the application under the code profiler."""
    from werkzeug.contrib.profiler import ProfilerMiddleware
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[length],
                                      profile_dir=profile_dir)
    app.run()


@manager.command
def deploy():
    """Run deployment tasks."""
    from flask.ext.migrate import upgrade
    from app.models import Role, User

    # migrate database to latest revision
    upgrade()

    # create user roles
    Role.insert_roles()

@manager.command
def make_admin(username):
  u = User.query.filter_by(username=username).first()
  u.role_id = 1
  print(u.username,'was made admin')
  db.session.commit()

@manager.command
def make_fakes():
  # Users at RIT
  if input('make fake users?').lower() == 'y':
    User.generate_fake(20, 8196)
  if input('make fake events?').lower() == 'y':
    Event.generate_fake(250, 8196)

@manager.command
def upcoming_notify():
  import datetime
  from app import mailer
  
  next_30 = datetime.datetime.utcnow() + datetime.timedelta(minutes=300)
  now = datetime.datetime.utcnow()
  events = Event.query.filter( Event.time > now ).filter(Event.time < next_30).all()
  for event in events:
    for user in event.attendees:
      mailer.notify_soon(user, event)
  
  

@manager.command
def importschools(fpath):
    """Import CSV file with all schools into database"""
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

if __name__ == '__main__':
    manager.run()
