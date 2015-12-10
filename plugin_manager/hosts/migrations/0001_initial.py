# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import plugin_manager.hosts.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='HistoryLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_update', models.DateTimeField(auto_now=True)),
                ('date_deleted', models.DateTimeField(null=True, blank=True)),
                ('updated', models.DateTimeField()),
                ('size', models.IntegerField()),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Host',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_update', models.DateTimeField(auto_now=True)),
                ('date_deleted', models.DateTimeField(null=True, blank=True)),
                ('name', models.CharField(help_text=b'DNS name or IP address', max_length=255, validators=[plugin_manager.hosts.models.SchemelessURLValidator()])),
                ('alias', models.CharField(help_text=b'Human readable value (optional)', max_length=255, null=True, blank=True)),
                ('ssh_username', models.CharField(help_text=b'SSH Username to upload the plugins', max_length=255, null=True, verbose_name=b'SSH Username', blank=True)),
                ('ssh_password', models.CharField(help_text=b'SSH Password to upload the plugins', max_length=255, null=True, verbose_name=b'SSH Password', blank=True)),
                ('jenkins_username', models.CharField(help_text=b'Jenkins Username to gather info of the plugins and issue restarts', max_length=255, null=True, verbose_name=b'Jenkins Username', blank=True)),
                ('jenkins_password', models.CharField(help_text=b'Jenkins Token to gather info of the plugins and issue restarts', max_length=255, null=True, verbose_name=b'Jenkins API Token', blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_update', models.DateTimeField(auto_now=True)),
                ('date_deleted', models.DateTimeField(null=True, blank=True)),
                ('name', models.CharField(help_text=b'Name', max_length=100)),
                ('path', models.CharField(help_text=b'Path folder', max_length=255)),
                ('host', models.ForeignKey(related_name=b'host_set', to='hosts.Host')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Plugin',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_update', models.DateTimeField(auto_now=True)),
                ('date_deleted', models.DateTimeField(null=True, blank=True)),
                ('name', models.CharField(max_length=255)),
                ('version', models.CharField(max_length=255)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='historylog',
            name='log',
            field=models.ForeignKey(to='hosts.Log'),
            preserve_default=True,
        ),
    ]
