from dateutil.parser import parse
from flask import render_template, session, redirect, url_for, current_app,\
  flash, jsonify, request
from flask.ext.login import login_user, login_required, current_user
from . import main
from .forms import EditProfileForm, MakeEventForm, SchoolSearchForm
from ..auth.forms import LoginForm, RegistrationForm
from .. import db
from ..models import User, Event, Location
from autocomplete.views import autocomplete_view


@main.route('/', methods=['GET', 'POST'])
def index():
  user = None
  if current_user.is_authenticated():
    events = Event.query.filter_by(location=current_user.location).order_by(Event.time.desc())
    return render_template('index.html', events=events)
  else:
    # Registration form
    register = RegistrationForm()

    if register.validate_on_submit():
      user = User()
      user.email = register.email.data
      user.username = register.username.data
      user.location = register.location.data
      user.password = register.password.data
      user.confirmed = True
      db.session.add(user)
      db.session.commit()
      return redirect(url_for('auth.login'))


    # School search form
    schoolSearch = SchoolSearchForm()

    if schoolSearch.validate_on_submit():
      return redirect(url_for('main.location', id=schoolSearch.location.data.id))

    # Login form
    login = LoginForm()
    if login.validate_on_submit():
      user = User.query.filter_by(email=login.email.data).first()
      if user is not None and user.verify_password(login.password.data):
        login_user(user, login.remember_me.data)
        return redirect(url_for('main.index'))
      flash('Invalid username or password.')

    return render_template('index.html', loginForm=login,\
        registerForm=register, \
        schoolSearchForm=schoolSearch)


## User stuff

## User profile
@main.route('/user/<username>')
def user(username):
  user = User.query.filter_by(username=username).first_or_404()
  return render_template('user.html', user=user, events=user.submitted)

## Edit profile page
@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
  form = EditProfileForm()
  if form.validate_on_submit():
    num = form.phone.data.replace(' ', '')
    if( num != ''):
      current_user.phone = num
    current_user.text_updates = form.text_updates.data
    current_user.location = form.location.data
    db.session.add(current_user)
    flash('Your profile has been updated.')
    return redirect(url_for('.user', username=current_user.username))
  form.phone.data = current_user.phone
  form.text_updates.data = current_user.text_updates
  form.location = current_user.location
  return render_template('edit_profile.html', form=form)

def find_loc(query):
  results = Location.query.filter(Location.name.like('%'+str(query)+'%')).limit(5)
  locs = []
  for loc in results:
    locs.append({'id':loc.id, 'title' : loc.name, 'data' : [] })
  return locs

@main.route('/autocomplete')
def autocomplete():
    return autocomplete_view(find_loc, 'autocomplete.html')

### Event stuff

## Event page
@main.route('/event/<int:id>', methods=['GET', 'POST'])
def event(id):
  event = Event.query.get_or_404(id)
  return render_template('event.html', event=event)

## Make event form
@main.route('/make-event', methods=['GET', 'POST'])
@login_required
def make_event():
  form = MakeEventForm()
  if form.validate_on_submit():
    event = Event(name=form.name.data, serving=form.serving.data,\
                  time=form.time.data, body=form.body.data,\
                  place=form.place.data,
                  author=current_user._get_current_object(),
                  location=current_user.location)
    db.session.add(event)
    return redirect(url_for('.index'))
  return render_template('make-event.html', form=form)

## Locations list page
@main.route('/locations')
def locations():
  locations = Location.query.order_by(Location.name.asc())
  return render_template('locations.html', locations=locations)

## Location page
@main.route('/location/<id>')
def location(id):
  location = Location.query.get_or_404(id)
  events = Events.future_events(location.location_id)
  return render_template('location.html', location=location, events=events)

# Attend Event
@main.route('/attend/<id>')
def attend(id):
  event = Event.query.get_or_404(id)
  if current_user.is_attending(id):
    flash('You are already attending %s!'% event.name)
    return redirect(url_for('.event', id=event.id))
  event.attend_event(current_user.id)
  flash('You are now attending %s!'% event.name)
  return redirect(url_for('.event', id=event.id))

# Unattend Event
@main.route('/unattend/<id>')
def unattend(id):
  event = Event.query.get_or_404(id)
  if not current_user.is_attending(id):
    flash('You aren\'t attending %s!'% event.name)
    return redirect(url_for('.event', id=event.id))
  event.unattend_event(current_user.id)
  flash('You are no longer attending %s!'% event.name)
  return redirect(url_for('.event', id=event.id))
