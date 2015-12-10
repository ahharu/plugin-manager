"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase

from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.core.cache import cache
from plugin_manager.accounts.models import PermissionProject, PermissionStage,\
    PermissionHost


from model_mommy import mommy

from plugin_manager.hosts.models import Host

User = get_user_model()


class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)


