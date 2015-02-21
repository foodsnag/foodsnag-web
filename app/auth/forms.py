from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User, Location
from autocomplete.forms import AutocompleteField

class LoginForm(Form):
  email = StringField('Email', validators=[Required(), Length(1, 64), Email()])
  password = PasswordField('Password', validators=[Required()])
  remember_me = BooleanField('Remember me')
  submit = SubmitField('Log In')

def get_loc_by_id(id):
    loc = Location.query.filter_by(id=id).first()
    return loc

class RegistrationForm(Form):
  email = StringField('Email', validators=[Required(), Length(1, 64), Email()])
  username = StringField('Username', validators=[
  Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
    'Usernames must have only letters, '
    'numbers, dots or underscores')])
  location = AutocompleteField('School',
        url='auth.autocomplete',
        get_label='name',
        getter=get_loc_by_id,
        validators=[Required()]
    )
  password = PasswordField('Password', validators=[
    Required(), EqualTo('password2', message='Passwords must match.')])
  password2 = PasswordField('Confirm password', validators=[Required()])
  submit = SubmitField('Register')

  def validate_email(self, field):
    pass
    if User.query.filter_by(email=field.data).first():
      raise ValidationError('Email already registered.')

  def validate_username(self, field):
    pass
    if User.query.filter_by(username=field.data).first():
      raise ValidationError('Username already in use.')

