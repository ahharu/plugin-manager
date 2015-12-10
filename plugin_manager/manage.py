#!/usr/bin/env python
import os, sys

# Adds the plugin_manager package from the working copy instead of site_packages
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == '__main__':

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
    sys.path.append(os.getcwd())

    from django.conf import settings

    if getattr(settings, 'SOCKETIO_ENABLED', False):
        from gevent import monkey
        monkey.patch_all()

    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
