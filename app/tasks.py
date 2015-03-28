"""
These are tasks used by celery workers to handle email notifications.

Need to have RabbitMQ and celery installed and running on the system.

Worker can be run as follows:
  celery -A tasks worker --loglevel=info --beat 

"""
from celery import Celery
from celery.task import periodic_task
from datetime import timedelta

app = Celery('tasks', backend='amqp', broker='amqp://')

app.conf.CELERY_TIMEZONE = 'America/New_York'


@periodic_task(run_every=timedelta(hours=10))
def daily_notify():
  """ Runs every day to notify users of daily events """
  print("Running the daily task!!!")

@app.task(name='tasks.event_notify')
def event_notify( name, time ):
  """ Notifies a user of an upcoming event """
  print("REMEMBER to go to that event,",name,"!! It's at",time)
  # Do some email stuff here
  # Then do some text notifications here
