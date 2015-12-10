
from plugin_manager.accounts.models import DeployUser
from django.db.models import Q


def get_filtered_user_queryset_from_filter_dict(filterdict):
    queryset = DeployUser.active_records.all()
    firstpass = True
    filterargs = ""

    for key, value in filterdict.iteritems():

        filterkwargs = {
            '{0}__{1}'.format(key, 'icontains'): value,
        }
        if firstpass:
            if key == 'user_level':
                filterkwargs = {
                    'groups__pk__in': value,
                }
            filterargs = Q(**filterkwargs)
            firstpass = False
        else:
            if key == 'user_level':
                filterkwargs = {
                    'groups__pk__in': value,
                }
            filterargs &= Q(**filterkwargs)
    return queryset.filter(filterargs)
