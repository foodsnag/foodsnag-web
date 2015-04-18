from flask import current_app, render_template
import requests

def notify_soon(user, event):
  """ Notify a user of an event happening soon """
  url = 'https://api.mailgun.net/v3/mg.foodsnag.com/messages'
  url = current_app.config['MG_URL'] 
  key = current_app.config['MG_KEY']
  to = user.email
  f = '{0} <{1}>'.format(current_app.config['MAILER_NAME'], current_app.config['MAILER_EMAIL'])
  subject = 'There\'s some food to snag!'
  text = render_template('email/reminder.txt', user=user, event=event)

  if current_app.config['TESTING']:
    print('Send email to',to)
  else:
    requests.post(url, auth=('api', key), data={
                  'from' : f ,
                  'to' : to,
                  'subject' : subject,
                  'text' : text } )
