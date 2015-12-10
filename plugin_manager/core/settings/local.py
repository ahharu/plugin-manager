# Local settings for core project.
LOCAL_SETTINGS = True
from plugin_manager.core.settings.base import *

DEBUG = True
ALLOWED_HOSTS = ['*']
TEMPLATE_DEBUG = True

########## Django Debug Toolbar Configuration
INSTALLED_APPS = INSTALLED_APPS + ('debug_toolbar',)
INTERNAL_IPS = ('127.0.0.1',)

HOOK_EVENTS = {}
HOOK_THREADING = False

# Add in the template timing toolbar
INSTALLED_APPS = INSTALLED_APPS + ('template_timings_panel',)

DEBUG_TOOLBAR_PANELS = (
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'debug_toolbar.panels.staticfiles.StaticFilesPanel',
    'debug_toolbar.panels.templates.TemplatesPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.logging.LoggingPanel',
    'debug_toolbar.panels.redirects.RedirectsPanel',
)


########## End Django Debug Toolbar Configuration

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',  # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'ktest3',  # Or path to database file if using sqlite3.
        'USER': 'ktest3',                             # Not used with sqlite3.
        'PASSWORD': 'ktest3',                         # Not used with sqlite3.
        'HOST': 'localhost',                             # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                             # Set to empty string for default. Not used with sqlite3.
    }
}

# Make this unique, and don't share it with anybody.
SECRET_KEY = '3(-(r&DUMMYKEYFIRJUNK@@#@#d=48-5p&(f'

if DEBUG:
    # Show emails in the console during developement.
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


import sys
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'stream': sys.stdout
        },
    },
    'loggers': {
        'mylogger': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True
        },
    }
}
