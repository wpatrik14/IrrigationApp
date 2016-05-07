"""
Django settings for IrrigationApp project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import djcelery

#import celery
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '^k1@-=i^uf+d@3o9@i#c!uszx79j0%&g!#@yudve7$*%b86f*y'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'kombu.transport.django',
    'djcelery',
    'IrrigationApp'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'IrrigationApp.urls'

WSGI_APPLICATION = 'IrrigationApp.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

#DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.sqlite3',
#        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#    # for sqlite write lock timeout
#    'OPTIONS': {
#        'timeout': 10,
#        } 
#    }
#}


DATABASES = {
   'default': {
       'ENGINE': 'django.db.backends.mysql',
        'NAME': 'IrrigationApp',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': 'localhost',   # Or an IP Address that your DB is hosted on
        'PORT': '3306',
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LOGIN_URL = 'showLogin/'
LOGOUT_URL = 'doLogout/'

STATIC_URL = '/static/'
TEMPLATE_DIRS = os.path.join(BASE_DIR,'templates'),
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Budapest'
USE_L10N = False
DATE_FORMAT = "Y-m-d"
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

#BROKER_URL = "amqp://guest:guest@localhost:5672/"
#CELERY_RESULT_BACKEND = "amqp"

#BROKER_BACKEND = "djkombu.transport.DatabaseTransport"
#BROKER_BACKEND = "django"

#CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'
#BROKER_URL = 'django://'

CELERY_IMPORTS = ('IrrigationApp.tasks')
from celery.schedules import crontab

CELERYBEAT_SCHEDULE = {
    'get_weather_datas': {
        'task': 'IrrigationApp.tasks.get_weather_datas',
        'schedule': crontab(minute=0, hour='*/1'),
    },
    'automation_control': {
        'task': 'IrrigationApp.tasks.automation_control',
        'schedule': crontab(minute='*/1'),
    },
    #===========================================================================
    # 'follow_irrigation_template': {
    #     'task': 'IrrigationApp.tasks.follow_irrigation_template',
    #     'schedule': crontab(minute=0, hour='*/24'),
    # },
    #===========================================================================
    #===========================================================================
    #'getSensorData': {
    #    'task': 'IrrigationApp.tasks.getSensorData',
    #    'schedule': crontab(minute=0, hour='*/1'),
    #},
    #===========================================================================
}

CELERY_TIMEZONE = 'Europe/Budapest'


# Tell celery to use your new serializer:
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

djcelery.setup_loader()
