import django_tables2 as tables

from plugin_manager.hosts import models
from plugin_manager.core.mixins.tables import ActionsColumn, PaginateTable, ActionsColumn2
from plugin_manager.accounts.models import DeployUser
from django.conf import settings
from django.core.urlresolvers import reverse_lazy, reverse


class HostTable(PaginateTable):
    actions = ActionsColumn([
        {'title': '<i class="glyphicon glyphicon-file"></i>', 'url': 'hosts_host_detail', 'args': [tables.A('pk')],
         'attrs':{'data-toggle': 'tooltip', 'title': 'View Host', 'data-delay': '{ "show": 300, "hide": 0 }'}},
        {'title': '<i class="glyphicon glyphicon-pencil"></i>', 'url': 'hosts_host_update', 'args': [tables.A('pk')],
         'attrs':{'data-toggle': 'tooltip', 'title': 'Edit Host', 'data-delay': '{ "show": 300, "hide": 0 }'}},
        {'title': '<i class="glyphicon glyphicon-trash"></i>', 'url': 'hosts_host_delete', 'args': [tables.A('pk')],
         'attrs':{'data-toggle': 'tooltip', 'title': 'Delete Host', 'data-delay': '{ "show": 300, "hide": 0 }'}},
    ], delimiter='&#160;&#160;&#160;')

    class Meta:
        model = models.Host
        attrs = {"class": "table table-striped"}
        exclude = ('id','jenkins_username','jenkins_password','ssh_username','ssh_password')


class HostMembersTable(PaginateTable):
    """Table used to show the members of a host

    Also provides actions for and delete"""

    role = tables.Column(accessor='role', verbose_name='User Level')

    def __init__(self, *args, **kwargs):
        host_id = kwargs.pop('host_id')

        self.base_columns['actions'] = ActionsColumn([
            {'title': '<i class="glyphicon glyphicon-trash"></i>', 'url': 'hosts_host_members_delete', 'args': [host_id, tables.A('pk')],
             'attrs':{'data-toggle': 'tooltip', 'title': 'Delete User', 'data-delay': '{ "show": 300, "hide": 0 }'}},
        ], delimiter='&#160;&#160;&#160;')

        super(HostMembersTable, self).__init__(*args, **kwargs)

    class Meta:
        model = DeployUser
        attrs = {"class": "table table-striped"}
        sequence = fields = (
            'first_name',
            'last_name',
            'role',
            'actions',
        )


class HostMembersAddTable(PaginateTable):
    """Table used to add members of a host

    Also provides actions for delete"""

    role = tables.Column(accessor='role', verbose_name='User Level')

    actions = tables.TemplateColumn("<a class='btn btn-default btn-primary btn-xs' id='add_{{ record.pk }}'data-original-title='View Deployment Details' data-delay='{ &quot;show&quot;: 300, &quot;hide&quot;: 0 }' data-toggle='tooltip' title='Add Member'>Add</a>")

    class Meta:
        model = DeployUser
        attrs = {"class": "table table-striped"}
        sequence = fields = (
            'first_name',
            'last_name',
            'role',
            'actions',
        )


class HostPluginsInstalledTable(PaginateTable):
    """Table used to show the members of a host

    Also provides actions for and delete"""

    name = tables.Column(verbose_name='Plugin Name')
    version = tables.Column(verbose_name='Plugin Version')

    actions = tables.TemplateColumn("<a></a>")




    def __init__(self, *args, **kwargs):

        host_id = kwargs.pop('host_id')

        table_pagination = {
        "per_page": getattr(settings, "NUM_RESULTS_PER_PAGE", None)}

        self.base_columns['actions'] = ActionsColumn2([
            {'title': 'Update Plugin', 'url': [tables.A('url')], 'args': [host_id, tables.A('name')],
             'attrs':{'data-toggle': 'tooltip', 'title': 'Update Plugin', 'data-delay': '{ "show": 300, "hide": 0 }'}},
            {'title': 'Delete Plugin', 'url': 'hosts_host_plugin_delete', 'args': [host_id, tables.A('name')],
             'attrs':{'data-toggle': 'tooltip', 'title': 'Delete Plugin', 'data-delay': '{ "show": 300, "hide": 0 }'}}
        ], delimiter='&#160;&#160;&#160;')

        super(HostPluginsInstalledTable, self).__init__(*args, **kwargs)

    class Meta:
        attrs = {"class": "table table-striped"}
        table_pagination = {
        "per_page": getattr(settings, "NUM_RESULTS_PER_PAGE", None)}
        sequence = fields = (
            'name',
            'version',
            'actions',
        )