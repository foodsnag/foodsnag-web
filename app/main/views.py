from datetime import datetime, timedelta
from dateutil import tz
from dateutil.parser import parse
from flask import render_template, session, redirect, url_for, current_app,\
  flash, jsonify, request
from flask.ext.login import login_user, login_required, current_user
from . import main
from .forms import EditProfileForm, SchoolSearchForm, MakeEventForm
from ..extensions import db
from ..models import User, Event, Location
from autocomplete.views import autocomplete_view
from sqlalchemy import func
from ..tasks import event_notify


@main.route('/', methods=['GET', 'POST'])
def index():
  user = None
  events = None
  if current_user.is_authenticated():
    events = Event.future_events(current_user.location_id)
    return render_template('index.html', events=events)
  else:
    # School search form
    schoolSearch = SchoolSearchForm(prefix="search")
    if schoolSearch.validate_on_submit():
      if hasattr(schoolSearch.location.data, 'id'):
        return redirect(url_for('main.location', id=schoolSearch.location.data.id))
    return render_template('index.html', schoolSearchForm=schoolSearch)


## User stuff

@main.route('/user/<username>')
def user(username):
  """
  User profile
  """
  user = User.query.filter_by(username=username).first_or_404()
  return render_template('user.html', user=user, events=user.submitted)

@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
  """
  Edit profile
  """
  form = EditProfileForm(email=current_user.email,
                        email_notifications=current_user.email_notifications,
                        location=current_user.location)

  if form.validate_on_submit():
    if form.location.data != '':
      current_user.location = form.location.data
    current_user.email = form.email.data
    current_user.email_notifications = form.email_notifications.data
    db.session.add(current_user)
    db.session.commit()
    flash('Your profile has been updated.')
    return redirect(url_for('.user', username=current_user.username))
  return render_template('edit_profile.html', form=form)

def find_loc(query):
  """
  Find location using a search query.
  Used for auto complete
  """
  results = Location.query.filter(Location.name.like('%'+str(query)+'%')).limit(5)
  locs = []
  for loc in results:
    locs.append({'id':loc.id, 'title' : loc.name, 'data' : [] })
  return locs

@main.route('/autocomplete')
def autocomplete():
    return autocomplete_view(find_loc, 'autocomplete.html')

### Event stuff

@main.route('/event/<int:id>', methods=['GET', 'POST'])
def event(id):
  """
  Event page
  """
  event = Event.query.get_or_404(id)
  return render_template('event.html', event=event)

## Make event form
@main.route('/make-event', methods=['GET', 'POST'])
@login_required
def make_event():
  """
  Make a new event page
  """
  form = MakeEventForm()
  if form.validate_on_submit():
    d = form.date.data
    t = form.time.data
    # Combine date and time
    t = datetime(datetime.now().year, d.month, d.day, t.hour, t.minute)
    event = Event(name=form.name.data, serving=form.serving.data,\
      time=t, body=form.body.data,\
      place=form.place.data,
      author=current_user._get_current_object(),
      location=current_user.location)

    # Create a notification event
    # Have to make local to utc
    to_zone = tz.tzutc()
    from_zone = tz.tzlocal()
    utc = t.replace(tzinfo=from_zone)
    alarm = utc.astimezone(to_zone)
    # Notify 30 min before event
    alarm = alarm - timedelta(minutes=30)
    #event_notify.apply_async( ( self ), eta=alarm )
    event_notify.apply_async( ( 'hi', ), delay=30 )

    db.session.add(event)
    db.session.commit()
    return redirect(url_for('main.index'))
  return render_template('make-event.html', form=form)


@main.route('/locations')
def locations():
  """
  Displays page of locations (currently not used)
  """
  locations = Location.query.order_by(Location.name.asc())
  return render_template('locations.html', locations=locations)

@main.route('/location/<id>')
def location(id):
  """
  Location page
  Shows events happening at a given location
  """
  location = Location.query.get_or_404(id)
  events = Event.future_events(location.id)
  return render_template('location.html', location=location, events=events)

@main.route('/attend/<id>')
def attend(id):
  """
  Attend event
  """
  event = Event.query.get_or_404(id)
  if current_user.is_attending(id):
    flash('You are already attending %s!'% event.name)
    return redirect(url_for('.event', id=event.id))
  event.attend_event(current_user.id)
  flash('You are now attending %s!'% event.name)
  return redirect(url_for('.event', id=event.id))

@main.route('/unattend/<id>')
def unattend(id):
  """
  Unattend event (remove from going list)
  """
  event = Event.query.get_or_404(id)
  if not current_user.is_attending(id):
    flash('You aren\'t attending %s!'% event.name)
    return redirect(url_for('.event', id=event.id))
  event.unattend_event(current_user.id)
  flash('You are no longer attending %s!'% event.name)
  return redirect(url_for('.event', id=event.id))
