import os
import os.path
import sys

# Add the project to the python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.pardir))
sys.stdout = sys.stderr

deployenv = os.getenv('deployenv')
env_dict = {
    'local': 'plugin_manager.core.settings.local',
    'pre': 'plugin_manager.core.settings.pre',
    'production': 'plugin_manager.core.settings.production',

}

os.environ.setdefault('DJANGO_SETTINGS_MODULE', env_dict[deployenv])

sys.path.append(os.getcwd())

from django.conf import settings

if getattr(settings, 'SOCKETIO_ENABLED', False):
    from gevent import monkey
    monkey.patch_all()

# Configure the application (Logan)
#from plugin_manager.utils.runner import configure
#configure()

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
