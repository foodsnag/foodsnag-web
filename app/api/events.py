from flask import jsonify, request
from .. import db
from ..models import Event
from . import api

@api.route('/event/<int:id>')
def get_event(id):
  event = Event.query.get_or_404(id)
  return jsonify(event.to_json())
