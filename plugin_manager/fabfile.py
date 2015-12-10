# -*- coding: utf-8 -*-
#from fabric.api import local, env
from fabric.api import *
from fabric.operations import run, put
import os
import uuid
import jenkins

PLUGIN_URL_BASE = "http://updates.jenkins-ci.org/download/plugins"

@task
def update_plugin(plugin_name,plugin_version):
    print("fabric launched")
    unique_fname = uuid.uuid4()
    jenkins_server = jenkins.Jenkins('http://'+env.host_string,env.jenkins_username,env.jenkins_password)
    local('mkdir /tmp/%s' % unique_fname)
    with lcd('/tmp/%s' % unique_fname), settings(warn_only=True):
        local('wget %s/%s/%s/%s.hpi' %(PLUGIN_URL_BASE,plugin_name,plugin_version,plugin_name))
        run('rm -rf /var/lib/jenkins/plugins/%s*' % plugin_name)
        put('%s.hpi' %(plugin_name),'/var/lib/jenkins/plugins')
        local('rm -rf /tmp/%s' % unique_fname)
    jenkins_server.quiet_down()

@task
def delete_plugin(plugin_name):
    with settings(warn_only=True):
        print("fabric launched")

        run('rm -rf /var/lib/jenkins/plugins/%s*' % plugin_name)
        jenkins_server = jenkins.Jenkins('http://'+env.host_string,env.jenkins_username,env.jenkins_password)
        jenkins_server.quiet_down()



@task
def upload_plugin(plugin_path):
    print("fabric launched")
    basename = os.path.basename(plugin_path)
    run('rm -rf /var/lib/jenkins/plugins/%s*' % basename)
    put('%s' %(plugin_path),'/var/lib/jenkins/plugins')
    local('rm -rf %s' % plugin_path)
    jenkins_server = jenkins.Jenkins('http://'+env.host_string,env.jenkins_username,env.jenkins_password)
    jenkins_server.quiet_down()
