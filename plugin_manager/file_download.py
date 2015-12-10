# -*- coding: utf-8 -*-
#from fabric.api import local, env
from fabric.api import *
from fabric.operations import run, put
from fabric.colors import blue, cyan, green, red, white, yellow, magenta
from fabric.decorators import task
from StringIO import StringIO
from datetime import date, datetime
from xml.etree import ElementTree as ET
import random
import time
from fabric.contrib.console import confirm
from fabtools import service
import os

now = datetime.today()

PATH_TO_STATIC_FILES = '/var/www/fabric/plugin_manager/core/public/static/'


class FileDownload():

    def get_url_to_download(self, path_to_file):
        with settings(warn_only=True):
            run("mkdir %stmp" % PATH_TO_STATIC_FILES)
            code = run("rsync -a %s %stmp/" % (path_to_file,
                                               PATH_TO_STATIC_FILES))
            if code == 0 or code == '':
                path = "http://%s/static/tmp/%s" % (env.hosts[0],
                                             os.path.basename(
                                             path_to_file))
            else:
                raise IOError()
        print(path)
        return path

    def clean_tmp_folder(self):
        with settings(warn_only=True):
            sudo("rm -r /var/www/fabric/plugin_manager/core/public/static/tmp/*")
