from datetime import datetime
from flask import jsonify, request
from .. import db
from ..models import Location, Event, User
from . import api

@api.route('/location/<int:id>')
def get_location(id):
  loc = Location.query.get(id)
  print(loc.to_json())
  return jsonify(loc.to_json())

# Returns lim locations for the location of with id loc_id 
# Sorts events by those occuring first
@api.route('/location/<int:loc_id>/events/<int:lim>')
def get_events_by_loc(loc_id, lim):
  if lim > 25:
    lim = 25
  events = Event.query.filter_by(location_id=loc_id).limit(lim)
  #events = events.filter_by(Event.time > datetime.utcnow).limit(lim)
  #events = Event.query.filter_by(timestamp > datetime.utcnow).limit(lim)
  #events = Event.query.filter_by(timestamp > 3).limit(lim)
  return jsonify({
    'events' : [ event.to_json() for event in events ]
  })

# Return up to lim user ids for location of id loc_id
@api.route('/location/<int:loc_id>/users/<int:lim>')
def get_users_by_loc(loc_id, lim):
  if lim > 25:
    lim = 25
  users = User.query.filter_by(location_id=loc_id).limit(lim)
  return jsonify({
    'users' : [ user.to_json() for user in users ]
  })
