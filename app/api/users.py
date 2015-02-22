from flask import jsonify, request
from .. import db
from ..models import User, Location, Event
from . import api

# Get user profile
@api.route('/user/<int:id>')
def get_user(id):
  user = User.query.get_or_404(id)
  event_count = user.events.count()

  json_post = user.to_json()
  json_post['num_events_created'] = event_count
  # TODO: Change when new model is available
  json_post['num_events_attended'] = event_count
  return jsonify(json_post)

# Returns lim events created by user with id u_id 
@api.route('/user/<int:u_id>/events/<int:lim>')
def get_events_by_user(u_id, lim):
  events = Event.query.filter_by(author_id=u_id).limit(lim)
  return jsonify({
    'events' : [ event.to_json() for event in events ]
  })

# Returns lim events attended by user with id u_id 
# TODO: Implement when new model available
@api.route('/user/<int:u_id>/attended/<int:lim>')
def get_attended_by_user(u_id, lim):
  pass
