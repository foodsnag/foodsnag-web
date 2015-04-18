from flask import current_app, render_template
import requests

def welcome(user):
  """ Send a welcome email to the user """
  url = current_app.config['MG_URL'] 
  key = current_app.config['MG_KEY']
  to = user.email
  f = '{0} <{1}>'.format(current_app.config['MAILER_NAME'], current_app.config['MAILER_EMAIL'])
  subject = 'Welcome to FoodSnag!'
  print('no fail')
  text = render_template('email/welcome.txt', user=user)

  if current_app.config['TESTING']:
    print('Send welcome email to', to)
    print(text)
  else:
    requests.post(url, auth=('api', key), data={
                  'from' : f ,
                  'to' : to,
                  'subject' : subject,
                  'text' : text } )


def reminder(user, event):
  """ Notify a user of an event happening soon """
  if( user.email_notifications ):
    url = current_app.config['MG_URL'] 
    key = current_app.config['MG_KEY']
    to = user.email
    f = '{0} <{1}>'.format(current_app.config['MAILER_NAME'], current_app.config['MAILER_EMAIL'])
    subject = 'There\'s some food to snag!'
    text = render_template('email/reminder.txt', user=user, event=event)

    if current_app.config['TESTING']:
      print('Send reminder to', to)
    else:
      requests.post(url, auth=('api', key), data={
                    'from' : f ,
                    'to' : to,
                    'subject' : subject,
                    'text' : text } )
