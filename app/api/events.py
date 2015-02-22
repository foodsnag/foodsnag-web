from flask import jsonify, request
from .. import db
from ..models import Event
from . import api

# Get event
@api.route('/event/<int:id>')
def get_event(id):
  event = Event.query.get_or_404(id)
  # TODO: Implement when the model updates
  attendees_count = 1

  json_post = event.to_json()
  # TODO: Change when new model is available
  json_post['num_attendees'] = attendees_count

  return jsonify(json_post)

# Returns lim users attending the event 
@api.route('/event/<int:id>/attending')
def get_attendees(id, lim):
  # TODO: Implement when new model available
  pass
