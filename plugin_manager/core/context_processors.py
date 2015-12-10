from django.contrib.auth import get_user_model

from plugin_manager.hosts.models import Host
from plugin_manager.accounts.models import DeployUser


def sidebar_lists(request):
    context = {}
    context['sidebar_hosts'] = Host.objects.all().order_by('-date_created')[:5]

    context['sidebar_users'] = get_user_model().objects.all().order_by('-date_created')[:5]
    return context