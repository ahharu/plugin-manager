# coding=utf-8

from __future__ import absolute_import

import os

from celery import Celery

from django.conf import settings

# set the default Django settings module for the 'celery' program.
deployenv = os.getenv('deployenv')
env_dict = {
    'local': 'plugin_manager.core.settings.local',
    'pre': 'plugin_manager.core.settings.pre',
    'production': 'plugin_manager.core.settings.production',

}
if not os.getenv('deployenv'):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'plugin_manager.core.settings.local')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', env_dict[deployenv])

app = Celery('plugin_manager')

# Using a string here means the worker will
# not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(bind=False)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
