"""
Custom user model for deployments.
"""

import urllib
import hashlib
import base64
import random

from authtools.models import AbstractEmailUser
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save

from .managers import DeployUserManager
from plugin_manager.hosts.models import Host
from plugin_manager.accounts.model_managers import DeployUserActiveManager
from plugin_manager.core.mixins.models import TrackingFields


class DeployUser(AbstractEmailUser, TrackingFields):
    """
    Custom user class for deployments. Email as username using
    django-custom-user.
    """

    AMELIA = 'amelia.min.css'
    CERULEAN = 'cerulean.min.css'
    COSMO = 'cosmo.min.css'
    CYBORG = 'cyborg.min.css'
    DARKLY = 'darkly.min.css'
    FLATLY = 'flatly.min.css'
    JOURNAL = 'journal.min.css'
    LUMEN = 'lumen.min.css'
    READABLE = 'readable.min.css'
    SIMPLEX = 'simplex.min.css'
    SLATE = 'slate.min.css'
    SPACELAB = 'spacelab.min.css'
    SUPERHERO = 'superhero.min.css'
    UNITED = 'united.min.css'
    YETI = 'yeti.min.css'

    TEMPLATES = (
        (AMELIA, 'Amelia'),
        (CERULEAN, 'Cerulean'),
        (COSMO, 'Cosmo'),
        (CYBORG, 'Cyborg'),
        (DARKLY, 'Darkly'),
        (FLATLY, 'Flatly'),
        (JOURNAL, 'Journal'),
        (LUMEN, 'Lumen'),
        (READABLE, 'Readable'),
        (SIMPLEX, 'Simplex'),
        (SLATE, 'Slate'),
        (SPACELAB, 'Spacelab'),
        (SUPERHERO, 'Superhero'),
        (UNITED, 'United'),
        (YETI, 'Yeti'),
    )

    active_records = DeployUserActiveManager()

    first_name = models.CharField(_('first name'), max_length=30, blank=False)
    last_name = models.CharField(_('last name'), max_length=30,
                                 blank=False)
    template = models.CharField(max_length=255, blank=True,
                                choices=TEMPLATES, default=YETI)

    objects = DeployUserManager()

    def __unicode__(self):
        return u'{} {}'.format(self.first_name, self.last_name)

    @property
    def role(self):
        """
        Assumes the user is only assigned to one role and return it
        """
        return self.group_strigify()

    def _get_groups(self):
        if not hasattr(self, '_cached_groups'):
            self._cached_groups = list(self.groups.values_list("name",
                                                               flat=True))
        return self._cached_groups

    def user_is_admin(self):
        if not self.pk:
            return False
        return "Admin" in self._get_groups()

    def user_is_deployer(self):
        if not self.pk:
            return False
        return "Deployer" in self._get_groups()

    def user_is_historian(self):
        if not self.pk:
            return False
        return "Historian" in self._get_groups()

    def group_strigify(self):
        """
        Converts this user's group(s) to a string and returns it.
        """
        return "/".join(self._get_groups())

    def gravatar(self, size=20):
        """
        Construct a gravatar image address for the user
        """
        default = "mm"

        gravatar_url = "http://www.gravatar.com/avatar/" + hashlib.md5(
            self.email.lower()).hexdigest() + "?"
        gravatar_url += urllib.urlencode({'d': default, 's': str(size)})

        return gravatar_url


class APIKey(models.Model):
    apikey = models.CharField(max_length=255, primary_key=True)
    deployuser = models.ForeignKey(DeployUser)

    class Meta:
        unique_together = (("apikey", "deployuser"),)

class PermissionHost(models.Model):
    user = models.ForeignKey(DeployUser)
    host = models.ForeignKey(Host)

    def __unicode__(self):
        return u'User: {} Host: {}'.format(self.user, self.host)


def generate_APIKey(sender, instance, created, **kwargs):
    if created:
        apikey = APIKey()
        apikey.apikey = base64.b64encode(hashlib.sha256(
            str(random.getrandbits(256))).digest(),
                                         random.choice(
                                             ['rA', 'aZ', 'gQ', 'hH', 'hG',
                                              'aR', 'DD'])).rstrip('==')
        apikey.deployuser = instance
        apikey.save()


post_save.connect(generate_APIKey, sender=DeployUser)
