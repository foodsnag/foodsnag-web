from flask import jsonify, request
from .. import db
from ..models import Location
from . import api

@api.route('/location/<int:id>')
def get_location(id):
  loc = Location.query.get(id)
  return jsonify(loc.to_json())

# Returns lim locations for the location of with id loc_id 
@api.route('/location/<int:loc_id>/events/<int:lim>')
def get_events_by_loc(loc_id, lim):
  events = Event.query.filter_by(location=id).limit(lim)
  return jsonify({
    'events' : [ event.to_json() for event in events ]
  })
