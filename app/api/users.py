from flask import jsonify, request
from .. import db
from ..models import User, Location
from . import api

@api.route('/user/<int:id>')
def get_user(id):
  print('hi')
  user = User.query.get_or_404(id)
  print(user)
  return jsonify(user.to_json())

# Returns lim events created by user with id u_id 
@api.route('/user/id/<int:u_id>/events/<int:lim>')
def get_events_by_user(u_id, lim):
  events = Event.query.filter_by(author_id=u_id).limit(lim)
  return jsonify({
    'events' : [ event.to_json() for event in events ]
  })
