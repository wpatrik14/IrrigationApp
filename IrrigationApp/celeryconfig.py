BROKER_URL = "amqp://guest:guest@localhost:5672/"
CELERY_RESULT_BACKEND = "amqp"

CELERY_IMPORTS = ('IrrigationApp.tasks')
from celery.schedules import crontab

CELERYBEAT_SCHEDULE = {
    'get_weather_datas': {
        'task': 'IrrigationApp.tasks.get_weather_datas',
        #'schedule': crontab(minute=0, hour='*/1'),
        'schedule': crontab(minute='*/15'),
    },
    'automation_control': {
        'task': 'IrrigationApp.tasks.automation_control',
        'schedule': crontab(minute='*/1'),
    },
    'scheduler': {
        'task': 'IrrigationApp.tasks.scheduler',
        'schedule': crontab(minute='*/1'),
    },
}

CELERY_TIMEZONE = 'Europe/London'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'