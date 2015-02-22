import datetime
from dateutil.parser import parse
from flask.ext.wtf import Form
from wtforms import StringField, TextAreaField, BooleanField, SelectField,\
  DateTimeField, SubmitField
from wtforms.validators import Required, Length, Email
from wtforms import ValidationError
from ..models import User, Event, Location
from autocomplete.forms import AutocompleteField

def get_loc_by_id(id):
  loc = Location.query.filter_by(id=id).first()
  return loc

class EditProfileForm(Form):
  text_updates = BooleanField('Send notifications through text')
  phone = StringField('Phone Number (To recieve event notifications)')
  location = AutocompleteField('School',
        url='auth.autocomplete',
        get_label='name',
        getter=get_loc_by_id,
        validators=[Required()]
    )
  submit = SubmitField('Submit')

  def validate_phone(self, field):
    if field.data != '' and User.query.filter_by(phone=num).first():
      raise ValidationError('That number is already in use.')

class SchoolSearchForm(Form):
  location = AutocompleteField(
        url='main.autocomplete',
        placeholder='Your school...',
        get_label='name',
        getter=get_loc_by_id,
        validators=[Required()]
    )
  submit = SubmitField('Submit')
