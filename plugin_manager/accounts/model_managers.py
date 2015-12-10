from django.db import models
from authtools.models import BaseUserManager
from plugin_manager.accounts.managers import DeployUserManager


class DeployUserActiveManager(DeployUserManager):
    def get_queryset(self):
        return super(DeployUserActiveManager, self).get_queryset().filter(date_deleted__isnull=True)
