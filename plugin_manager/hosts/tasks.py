# coding=utf-8
from __future__ import absolute_import

from celery import shared_task, task
from django.conf import settings
from django.core.mail import send_mail

from plugin_manager.hosts.util import build_command_update_plugin,\
    build_command_delete_plugin, build_command_upload_plugin
from celery.task.sets import subtask
from celery.task import task
import subprocess

@shared_task
def update_plugin(abort_on_prompts=True, *args, **kwargs):

    subprocess.Popen(
        build_command_update_plugin(kwargs.get('host'),
                                    kwargs.get('username'),
                                    kwargs.get('password'),
                                    kwargs.get('jenkins_username'),
                                    kwargs.get('jenkins_password'),
                                    kwargs.get('plugin_name'),
                                    kwargs.get('plugin_version')),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        executable="/bin/bash"
    )

@shared_task
def delete_plugin(abort_on_prompts=True, *args, **kwargs):
    subprocess.Popen(


        build_command_delete_plugin(kwargs.get('host'),
                                    kwargs.get('username'),
                                    kwargs.get('password'),
                                    kwargs.get('jenkins_username'),
                                    kwargs.get('jenkins_password'),
                                    kwargs.get('plugin_name')),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        executable="/bin/bash"
    )

@shared_task
def upload_plugin(abort_on_prompts=True, *args, **kwargs):

    subprocess.Popen(


        build_command_upload_plugin(kwargs.get('host'),
                                    kwargs.get('username'),
                                    kwargs.get('password'),
                                    kwargs.get('jenkins_username'),
                                    kwargs.get('jenkins_password'),
                                    kwargs.get('plugin_name'),
                                    kwargs.get('file_path')),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        executable="/bin/bash"
    )

