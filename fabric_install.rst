Fabric Bolt
===========

.. image:: https://travis-ci.org/worthwhile/plugin_manager.png?branch=master
        :target: https://travis-ci.org/worthwhile/plugin_manager

.. image:: https://coveralls.io/repos/worthwhile/plugin_manager/badge.png?branch=master
        :target: https://coveralls.io/r/worthwhile/plugin_manager?branch=master

| **tl;dr**
| A web interface for fabric deployments.

Fabric Bolt is a Python/Django project that allows you to deploy code stored in source control (a project) to a target server (host).
Fabric Bolt provides convenient web interfaces to configure both the projects and the hosts. Additionally, deployment history and
logs are stored so that you know who, what, where, when, and why something was deployed.

Documentation found at http://plugin_manager.readthedocs.org/en/latest/

.. image:: https://raw.github.com/worthwhile/plugin_manager/master/docs/images/Screen%20Shot%202013-09-29%20at%207.42.18%20PM.png

Quickstart
----------

These steps are designed to get you rolling quickly, but more complete install/setup information is provided in our `documentation
<http://plugin_manager.readthedocs.org/en/latest/>`_.

1. Clone git repo::

    https://<yourUsername>@scm.scytl.net/stash/scm/devsol/fabric.git

2. Install the requirements::

    pip install -r plugin_manager/requirements/local.txt

3. Modify generated settings file to enter database settings.

    its on /plugin_manager/core/settings/local.txt

4. Sync db ::

    python plugin_manager/manage.py syncdb


5. Migrate DB::

    python plugin_manager/manage.py migrate

5. Run Celery::

    celery -A plugin_manager.core.celery.app worker --loglevel=info

8. Run Server::

    python plugin_manager/manage.py runserver




Note:

If you have created a settings file at a different location than the default, you can use the --config option on any
command (besides the init command) to specify the custom file path. Alternatively, you can set an env variable: plugin_manager_CONF.

Authors
-------

* Dan Dietz (paperreduction)
* Jared Proffitt (jproffitt)
* Nathaniel Pardington (npardington)


Bolting web applications to servers since 2013 :: Deploy Happy!
