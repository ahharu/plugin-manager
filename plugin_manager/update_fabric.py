# -*- coding: utf-8 -*-
#from fabric.api import local, env
from fabric.api import *
from fabric.operations import run, put
import os
import jenkinsapi
import uuid


PLUGIN_URL_BASE = "http://updates.jenkins-ci.org/download/plugins"

@task
def update_plugin(plugin_name,plugin_version):
    print("fabric launched")
    unique_fname = uuid.uuid4()

    local('mkdir /tmp/%s' % unique_fname)
    with lcd('/tmp/%s' % unique_fname):
        local('wget %s/%s/%s/%s.hpi' %(PLUGIN_URL_BASE,plugin_name,plugin_version,plugin_name))
        run('rm -rf /var/lib/jenkins/plugins/%s*' % plugin_name)
        put('%s.hpi' %(plugin_name),'/var/lib/jenkins/plugins')
        local('rm -rf /tmp/%s' % unique_fname)