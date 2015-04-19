import datetime
from dateutil.parser import parse
from flask.ext.wtf import Form
from wtforms import StringField, TextAreaField, BooleanField, SelectField,\
  DateTimeField, SubmitField
from wtforms.validators import Required, Length, Email
from wtforms import ValidationError
from flask.ext.login import current_user
from ..models import User, Event, Location
from autocomplete.forms import AutocompleteField

def get_loc_by_id(id):
  loc = Location.query.filter_by(id=id).first()
  return loc

class EditProfileForm(Form):
  email = StringField('Email', validators=[Required(), Length(1, 64), Email()])
  location = AutocompleteField(
        label='Search for your school',
        url='main.autocomplete',
        placeholder='',
        get_label='name',
        getter=get_loc_by_id
  )
  email_notifications = BooleanField('Email me about upcoming events')
  submit = SubmitField('Submit')

class MakeEventForm(Form):
  name = StringField('What is the event?', validators=[Required()])
  food_types = [("Pizza","Pizza"), ("Fruit","Fruit"), ("Breakfast","Breakfast"),
    ("Burgers","Burgers"), ("Candy","Candy"), ("Ice cream","Ice cream"), ("Drinks","Drinks"), ("Alcohol","Alcohol"), ("Chicken","Chicken"), ("Cake","Cake"), ("BBQ","BBQ"), ("Coffee","Coffee"),
    ("Tea","Tea")]
  serving = SelectField('', choices=food_types)
  place = StringField('Where is this happening (Building/room)?',
    validators=[Required()])

  now = datetime.datetime.now()#.strftime('%m-%d %H:%M')
  date = DateTimeField('What date is this happening?',
    default=now, format='%A %B %d')

  twelve = datetime.datetime(now.year, now.month, now.day, 12)
  time = DateTimeField('When time is this happening?',
    default=twelve, format='%I:%M %p')
  
  body = StringField('Anything else we should know?')
  submit = SubmitField('Submit')

  def validate_date(self, field):
    pass
    #if field.data < datetime.datetime.now():
    # raise ValidationError('Time must be in the future')

class SchoolSearchForm(Form):
  location = AutocompleteField(
        label='Search for your school',
        url='main.autocomplete',
        placeholder='',
        get_label='name',
        getter=get_loc_by_id
    )
  submit = SubmitField('Submit')
