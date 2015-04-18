"""
These are tasks used by celery workers to handle email notifications.

Need to have RabbitMQ and celery installed and running on the system.

Worker can be run as follows:
  celery -A tasks worker --loglevel=info --beat 

"""
from .extensions import celery, db
from celery.task import periodic_task
from datetime import timedelta
from .models import User, Event

@periodic_task(run_every=timedelta(hours=24))
def daily_notify():
  """ Runs every day to notify users of daily events """
  print("Running the daily task!!!")

@periodic_task(run_every=timedelta(seconds=10))
def upcoming_notify():
  print('hi')
  print( User.query.get().limit(10) )

@celery.task(name='tasks.event_notify')
def event_notify( name, time ):
  """ Notifies a user of an upcoming event """
  print("REMEMBER to go to that event,",name,"!! It's at",time)
  # Do some email stuff here
  # Then do some text notifications here
