from flask import render_template, redirect, request, url_for, flash, jsonify
from flask.ext.login import login_user, logout_user, login_required, current_user
from . import auth
from .. import db
from ..models import User, Location
from .forms import LoginForm, RegistrationForm
from autocomplete.views import autocomplete_view
from sqlalchemy import func


@auth.route('/login', methods=['GET', 'POST'])
def login():
  form = LoginForm()
  if form.validate_on_submit():
    user = User.query.filter(func.lower(User.email) == func.lower(form.email.data)).first()
    if user is None:
        user = User.query.filter(func.lower(User.username) == func.lower(form.email.data)).first()
    if user is not None and user.verify_password(form.password.data):
      login_user(user, form.remember_me.data)
      flash('Hey, {0}!'.format(user.username))
      return redirect(request.args.get('next') or url_for('main.index'))
    flash('Invalid username or password')
  return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
  logout_user()
  flash('You have been logged out.')
  return redirect(url_for('main.index'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
  form = RegistrationForm()
  if form.validate_on_submit():
    user = User()
    user.email = form.email.data
    user.username = form.username.data
    user.location = form.location.data
    user.email_notifications = form.email_notifications.data
    user.password = form.password.data
    user.confirmed = True
    db.session.add(user)
    db.session.commit()
    #token = user.generate_confirmation_token()
    #send_email(user.email, 'Confirm Your Account',
    #           'auth/email/confirm', user=user, token=token)
    #flash('A confirmation email has been sent to you by email.')
    return redirect(url_for('auth.login'))
  return render_template('auth/register.html', form=form)

def find_loc(query):
  results = Location.query.filter(Location.name.like('%'+str(query)+'%')).limit(5)
  locs = []
  for loc in results:
    locs.append({'id':loc.id, 'title' : loc.name, 'data' : [] })
  return locs

@auth.route('/autocomplete')
def autocomplete():
    return autocomplete_view(find_loc, 'autocomplete.html')
