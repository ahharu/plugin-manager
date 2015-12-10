from logan.runner import run_app, configure_app

import sys
import base64
import os

KEY_LENGTH = 40


CONFIG_TEMPLATE = """

from plugin_manager.core.settings.base import *

CONF_ROOT = os.path.dirname(__file__)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',

        'NAME': os.path.join(CONF_ROOT, 'plugin_manager.db'),
        'USER': 'sqlite3',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

SECRET_KEY = %(default_key)r

"""


def generate_settings():
    output = CONFIG_TEMPLATE % dict(
        default_key=base64.b64encode(os.urandom(KEY_LENGTH)),
    )

    return output


def configure():
    configure_app(
        project='plugin_manager',
        default_config_path='~/.plugin_manager/settings.py',
        default_settings='plugin_manager.core.settings.base',
        settings_initializer=generate_settings,
        #settings_envvar='plugin_manager_CONF',
    )


def main(progname=sys.argv[0]):
    run_app(
        project='plugin_manager',
        default_config_path='~/.plugin_manager/settings.py',
        default_settings='plugin_manager.core.settings.base',
        settings_initializer=generate_settings,
        settings_envvar='plugin_manager_CONF',
    )

if __name__ == '__main__':
    main()
