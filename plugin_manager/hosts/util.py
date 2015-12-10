import os
import re
import subprocess
from urlparse import urlparse

from django.utils.text import slugify
from django.conf import settings
from django.core.cache import cache
from django.contrib import messages
from django.shortcuts import redirect
from virtualenv import create_environment
from plugin_manager.accounts.models import PermissionHost


"""
These options are passed to Fabric as:
fab task --abort-on-prompts=True --user=root ...
"""
fabric_special_options = ['no_agent', 'forward-agent', 'config',
                          'disable-known-hosts', 'keepalive', 'password',
                          'parallel', 'no-pty', 'reject-unknown-hosts',
                          'skip-bad-hosts', 'timeout', 'command-timeout',
                          'user', 'warn-only', 'pool-size']


def check_output_with_ssh_key(command):
    if getattr(settings, 'GIT_SSH_KEY_LOCATION', None):
        return subprocess.check_output(
            'ssh-agent bash -c "ssh-add {};{}"'.format(
                settings.GIT_SSH_KEY_LOCATION, command),
            shell=True
        )
    else:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            shell=True,
            executable="/bin/bash"
        )
        out = process.communicate()[0]
        return out


def isUserAllowed(user, perm):
    return True if user.has_perm(
        perm) or user.is_superuser else False


def update_project_git(project, cache_dir, repo_dir):
    if not os.path.exists(repo_dir):
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        parsedout = urlparse(project.repo_url)
        authpart = ""
        if (project.repo_username):
            authpart += project.repo_username
            if (project.repo_password):
                authpart += ":" + project.repo_password
            authpart += "@"

        check_output_with_ssh_key(
            'git config --global credential.helper cache')
        check_output_with_ssh_key(
            "git config --global credential.helper 'cache --timeout=999999999999'")
        check_output_with_ssh_key(
            'git clone {}://{}{}{} {}'.format(parsedout.scheme, authpart,
                                              parsedout.netloc, parsedout.path,
                                              repo_dir))
    else:
        check_output_with_ssh_key(
            'cd {0};git stash;git pull'.format(repo_dir)
        )


def setup_virtual_env_if_needed(repo_dir):
    env_dir = os.path.join(repo_dir, 'env')
    if not os.path.exists(env_dir):
        os.makedirs(env_dir)
        create_environment(env_dir)


def update_project_requirements(project, repo_dir, activate_loc):
    pip_installs = ' '.join(project.fabfile_requirements.splitlines())

    check_output_with_ssh_key(
        'source {} && cd {};pip install {}'.format(activate_loc, repo_dir,
                                                   pip_installs))


def get_fabfile_path(project):
    if project.use_repo_fabfile:
        cache_key = 'project_{}_fabfile_path'.format(project.pk)
        cached_result = cache.get(cache_key)

        if cached_result:
            return cached_result

        cache_dir = os.path.join(settings.PUBLIC_DIR, '.repo_caches')
        repo_dir = os.path.join(cache_dir, slugify(project.name))

        update_project_git(project, cache_dir, repo_dir)
        setup_virtual_env_if_needed(repo_dir)
        activate_loc = os.path.join(repo_dir, 'env', 'bin', 'activate')

        update_project_requirements(project, repo_dir, activate_loc)

        result = os.path.join(repo_dir, 'fabfile.py'), activate_loc
        cache.set(cache_key, result, settings.FABRIC_TASK_CACHE_TIMEOUT)
        return result
    else:
        return settings.FABFILE_PATH, None


def parse_task_details(name, task_output):
    lines = task_output.splitlines()
    docstring = '\n'.join([line.strip() for line in lines[2:-2]]).strip()
    arguments_line = lines[-2].strip()

    if docstring == 'No docstring provided':
        docstring = None

    arguments_line = arguments_line[11:].strip()

    arguments = []

    if arguments_line:
        for arg in arguments_line.split(', '):
            m = re.match(r"^([^=]+)(=(\'?)([^']*)\3)?$", arg)

            if m.group(2):  # found argument with default value
                if m.group(3) == "'":  # default value is a string
                    arguments.append((m.group(1), m.group(4)))
                else:  # found an argument with some other default value.
                    # all fab arguments are translated to strings, so this doesnt make sense. Ignore the default.
                    arguments.append(m.group(1))
            else:
                arguments.append(m.group(1))

    return name, docstring, arguments








def clean_key_string(key):
    key = key.replace('"', '\\"')  # escape double quotes
    key = key.replace(',',
                      '\,')  # escape commas, that would be adding a new value
    key = key.replace('=',
                      '\=')  # escape = because that would be setting a new key

    return key


def clean_value_string(value):
    value = value.replace('"', '\\"')  # escape double quotes
    value = value.replace(',',
                          '\,')  # escape commas, that would be adding a new value
    value = value.replace('=',
                          '\=')  # escape = because that would be setting a new key

    return value


def clean_arg_key_string(key):
    # this has to be a valid python function argument, so we can get pretty strict here
    key = re.sub(r'[^0-9a-zA-Z_]', '',
                 key)  # remove anything that isn't a number, letter, or underscore

    return key


def get_key_value_string(key, config):
    key = clean_key_string(key)

    if config.data_type == config.BOOLEAN_TYPE:
        return key + ('' if config.get_value() else '=')
    elif config.data_type == config.NUMBER_TYPE:
        return key + '=' + str(config.get_value())
    else:
        return '{}={}'.format(key, clean_value_string(config.get_value()))


def get_key_value_string_custom(key, config):
    key = clean_key_string(key)
    return '{}={}'.format(key, clean_value_string(config))


def update_config_values_from_session(configs, session):
    configs = configs.copy()

    for key, config in configs.iteritems():
        if session.get('configuration_values', {}).get(key, None) is not None:
            config.set_value(session['configuration_values'][key])
            del session['configuration_values'][key]

    arg_values = session.get('configuration_values', {})

    return configs, arg_values



def build_command_upload_files(list_of_logs, host, username, password,
                               abort_on_prompts=True):
    # Get the dictionary of configurations for this stage
    configs = {'user': username, 'password': password}

    nonewlinelist = list_of_logs.replace('\n', ';')

    task_args = [('log_path_list', nonewlinelist)]
    task_configs = [key for key, config in configs.iteritems()]

    command_to_config = {x.replace('-', '_'): x for x in
                         fabric_special_options}

    # Take the special env variables out
    normal_task_configs = list(
        set(task_configs) - set(command_to_config.keys()))

    # Special ones get set a different way
    special_task_configs = list(
        set(task_configs) & set(command_to_config.keys()))

    command = 'fab ' + 'upload_logs_list'

    task_args = list(set(task_args))

    if task_args:
        key_value_strings = []
        for key_ in task_args:
            if isinstance(key_, tuple):
                key = key_[0]
            else:
                key = key_

            if key in configs:
                value = unicode(configs[key].get_value())
            else:
                value = unicode(key_[1])

            cleaned_key = clean_arg_key_string(key)
            value = clean_value_string(value)
            key_value_strings.append('{}="{}"'.format(cleaned_key, value))

        if key_value_strings:
            command += ':'
            command += ','.join(key_value_strings)

    if normal_task_configs:
        command += ' --set '
        command += '"' + ','.join(
            get_key_value_string_custom(key, configs[key]) for key in
            normal_task_configs) + '"'

    if special_task_configs:
        for key in special_task_configs:
            command += ' --' + get_key_value_string_custom(
                command_to_config[key], configs[key])

    if abort_on_prompts:
        command += ' --abort-on-prompts'

    hosts = host
    if hosts:
        command += ' --hosts=' + host.name

    command += ' --fabfile=%s' % os.getenv('fabfile_utils')

    return command

def build_command_update_plugin(host, username, password,jenkins_username,jenkins_password,
                               plugin_name,plugin_version,abort_on_prompts=True):
    # Get the dictionary of configurations for this stage
    configs = {'user': username, 'password': password,
               'jenkins_username': jenkins_username, 'jenkins_password': jenkins_password}

    task_args = [('plugin_name', plugin_name),('plugin_version',plugin_version)]
    task_configs = [key for key, config in configs.iteritems()]

    command_to_config = {x.replace('-', '_'): x for x in
                         fabric_special_options}

    # Take the special env variables out
    normal_task_configs = list(
        set(task_configs) - set(command_to_config.keys()))

    # Special ones get set a different way
    special_task_configs = list(
        set(task_configs) & set(command_to_config.keys()))

    command = 'fab ' + 'update_plugin'

    task_args = list(set(task_args))

    if task_args:
        key_value_strings = []
        for key_ in task_args:
            if isinstance(key_, tuple):
                key = key_[0]
            else:
                key = key_

            if key in configs:
                value = unicode(configs[key].get_value())
            else:
                value = unicode(key_[1])

            cleaned_key = clean_arg_key_string(key)
            value = clean_value_string(value)
            key_value_strings.append('{}="{}"'.format(cleaned_key, value))

        if key_value_strings:
            command += ':'
            command += ','.join(key_value_strings)

    if normal_task_configs:
        command += ' --set '
        command += '"' + ','.join(
            get_key_value_string_custom(key, configs[key]) for key in
            normal_task_configs) + '"'

    if special_task_configs:
        for key in special_task_configs:
            command += ' --' + get_key_value_string_custom(
                command_to_config[key], configs[key])

    if abort_on_prompts:
        command += ' --abort-on-prompts'

    hosts = host
    if hosts:
        command += ' --hosts=' + host.name

    command += ' --fabfile=%s' % 'plugin_manager/fabfile.py'

    return command

def build_command_delete_plugin(host, username, password,jenkins_username,jenkins_password,
                               plugin_name,abort_on_prompts=True):
    # Get the dictionary of configurations for this stage
    configs = {'user': username, 'password': password,
               'jenkins_username': jenkins_username, 'jenkins_password': jenkins_password}

    task_args = [('plugin_name', plugin_name)]
    task_configs = [key for key, config in configs.iteritems()]

    command_to_config = {x.replace('-', '_'): x for x in
                         fabric_special_options}

    # Take the special env variables out
    normal_task_configs = list(
        set(task_configs) - set(command_to_config.keys()))

    # Special ones get set a different way
    special_task_configs = list(
        set(task_configs) & set(command_to_config.keys()))

    command = 'fab ' + 'delete_plugin'

    task_args = list(set(task_args))

    if task_args:
        key_value_strings = []
        for key_ in task_args:
            if isinstance(key_, tuple):
                key = key_[0]
            else:
                key = key_

            if key in configs:
                value = unicode(configs[key].get_value())
            else:
                value = unicode(key_[1])

            cleaned_key = clean_arg_key_string(key)
            value = clean_value_string(value)
            key_value_strings.append('{}="{}"'.format(cleaned_key, value))

        if key_value_strings:
            command += ':'
            command += ','.join(key_value_strings)

    if normal_task_configs:
        command += ' --set '
        command += '"' + ','.join(
            get_key_value_string_custom(key, configs[key]) for key in
            normal_task_configs) + '"'

    if special_task_configs:
        for key in special_task_configs:
            command += ' --' + get_key_value_string_custom(
                command_to_config[key], configs[key])

    if abort_on_prompts:
        command += ' --abort-on-prompts'

    hosts = host
    if hosts:
        command += ' --hosts=' + host.name

    command += ' --fabfile=%s' % 'plugin_manager/fabfile.py'

    return command


def build_command_upload_plugin(host, username, password,jenkins_username,jenkins_password,
                               plugin_name,file_path,abort_on_prompts=True):
    # Get the dictionary of configurations for this stage
    configs = {'user': username, 'password': password,
               'jenkins_username': jenkins_username, 'jenkins_password': jenkins_password}

    task_args = [('plugin_path', file_path)]
    task_configs = [key for key, config in configs.iteritems()]

    command_to_config = {x.replace('-', '_'): x for x in
                         fabric_special_options}

    # Take the special env variables out
    normal_task_configs = list(
        set(task_configs) - set(command_to_config.keys()))

    # Special ones get set a different way
    special_task_configs = list(
        set(task_configs) & set(command_to_config.keys()))

    command = 'fab ' + 'upload_plugin'

    task_args = list(set(task_args))

    if task_args:
        key_value_strings = []
        for key_ in task_args:
            if isinstance(key_, tuple):
                key = key_[0]
            else:
                key = key_

            if key in configs:
                value = unicode(configs[key].get_value())
            else:
                value = unicode(key_[1])

            cleaned_key = clean_arg_key_string(key)
            value = clean_value_string(value)
            key_value_strings.append('{}="{}"'.format(cleaned_key, value))

        if key_value_strings:
            command += ':'
            command += ','.join(key_value_strings)

    if normal_task_configs:
        command += ' --set '
        command += '"' + ','.join(
            get_key_value_string_custom(key, configs[key]) for key in
            normal_task_configs) + '"'

    if special_task_configs:
        for key in special_task_configs:
            command += ' --' + get_key_value_string_custom(
                command_to_config[key], configs[key])

    if abort_on_prompts:
        command += ' --abort-on-prompts'

    hosts = host
    if hosts:
        command += ' --hosts=' + host.name

    command += ' --fabfile=%s' % 'plugin_manager/fabfile.py'

    return command

def build_command_cron(stage, list_of_logs, host, abort_on_prompts=True):
    # Get the dictionary of configurations for this stage
    configs = stage.get_configurations()

    nonewlinelist = list_of_logs.replace('\n', ';')

    task_args = [('log_path_list', nonewlinelist), ('hostname', host.name),
                 ('stage', stage.name), ('project', stage.project.name)]
    task_configs = [key for key, config in configs.iteritems() if
                    not config.task_argument]

    command_to_config = {x.replace('-', '_'): x for x in
                         fabric_special_options}

    # Take the special env variables out
    normal_task_configs = list(
        set(task_configs) - set(command_to_config.keys()))

    # Special ones get set a different way
    special_task_configs = list(
        set(task_configs) & set(command_to_config.keys()))

    command = 'fab ' + 'upload_logs_list'

    task_args = list(set(task_args))

    if task_args:
        key_value_strings = []
        for key_ in task_args:
            if isinstance(key_, tuple):
                key = key_[0]
            else:
                key = key_

            if key in configs:
                value = unicode(configs[key].get_value())
            else:
                value = unicode(key_[1])

            cleaned_key = clean_arg_key_string(key)
            value = clean_value_string(value)
            key_value_strings.append('{}="{}"'.format(cleaned_key, value))

        if key_value_strings:
            command += ':'
            command += ','.join(key_value_strings)

    if normal_task_configs:
        command += ' --set '
        command += '"' + ','.join(
            get_key_value_string(key, configs[key]) for key in
            normal_task_configs) + '"'

    if special_task_configs:
        for key in special_task_configs:
            command += ' --' + get_key_value_string(command_to_config[key],
                                                    configs[key])

    if abort_on_prompts:
        command += ' --abort-on-prompts'

    hosts = host
    if hosts:
        command += ' --hosts=' + host.name

    fabfile_path, active_loc = get_fabfile_path(stage.project)
    command += ' --fabfile=/home/alruiz/tmp/myfab.py'

    return command


def getAdvancedPermissionBlock(request, permission_required=None,
                               instance=None):
    advPermGood = True
    if not instance or request.user.is_superuser:
        advPermGood = True

    elif instance.__class__.__name__.lower() == 'host':
        advPermGood = PermissionHost.objects.filter(user=request.user,
                                                    host=instance).exists()
    if request.user.is_authenticated():
        if permission_required is not None:
            for perm in permission_required:
                if not request.user.has_perm(
                        perm) or not advPermGood:
                    string_msg = 'You are not authorized\
                                  to access to this page.'
                    messages.add_message(
                        request, messages.ERROR, string_msg)
                    referer = request.META.get('HTTP_REFERER', '/')
                    return redirect(referer)
    else:
        return None