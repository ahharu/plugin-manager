import re

from django.db import models
from django.core.validators import RegexValidator

from plugin_manager.core.mixins.models import TrackingFields


class SchemelessURLValidator(RegexValidator):
    regex = re.compile(
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|'
        r'[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'  # ...or ipv4
        r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'  # ...or ipv6
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)


class Plugin(TrackingFields, models.Model):

    name = models.CharField(max_length=255)
    version = models.CharField(max_length=255)




class Host(TrackingFields, models.Model):
    """Defines a Host that deployments can be made to"""

    name = models.CharField(max_length=255, help_text='DNS name or IP address',
                            validators=[SchemelessURLValidator()])

    alias = models.CharField(
        blank=True,
        null=True,
        max_length=255,
        help_text='Human readable value (optional)',
    )

    ssh_username = models.CharField(
        blank=True,
        null=True,
        max_length=255,
        help_text='SSH Username to upload the plugins',
        verbose_name='SSH Username'
    )

    ssh_password = models.CharField(
        blank=True,
        null=True,
        max_length=255,
        help_text='SSH Password to upload the plugins',
        verbose_name='SSH Password'
    )

    jenkins_username = models.CharField(
        blank=True,
        null=True,
        max_length=255,
        help_text='Jenkins Username to gather info of the plugins and issue restarts',
        verbose_name='Jenkins Username'
    )

    jenkins_password = models.CharField(
        blank=True,
        null=True,
        max_length=255,
        help_text='Jenkins Token to gather info of the plugins and issue restarts',
        verbose_name='Jenkins API Token'
    )

    def __unicode__(self):
        return self.alias or self.name


class Log(TrackingFields, models.Model):
    name = models.CharField(max_length=100, help_text='Name')
    path = models.CharField(max_length=255, help_text="Path folder")
    host = models.ForeignKey(Host, related_name="host_set")

    def __unicode__(self):
        return "%s, %s" % (self.host, self.path)


class HistoryLog(TrackingFields, models.Model):
    updated = models.DateTimeField()
    size = models.IntegerField()
    log = models.ForeignKey(Log)

    def __unicode__(self):
        return "%s, %s, %s" % (self.log, self.size, self.updated)
