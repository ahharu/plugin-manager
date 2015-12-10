
from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import redirect

from django.contrib.auth.decorators import permission_required

from braces.views import GroupRequiredMixin, PermissionRequiredMixin



class MultipleGroupRequiredMixin(GroupRequiredMixin):

    def check_membership(self, group):
        """ Check required group(s) """
        user_groups = self.request.user.groups.values_list("name", flat=True)
        if isinstance(group, (list, tuple)):
            for req_group in group:
                if req_group in user_groups:
                    return True

        is_member = group in user_groups

        return is_member

    def dispatch(self, request, *args, **kwargs):
        self.request = request

        if self.request.user.is_authenticated():
            if not self.check_membership(
                    self.get_group_required()):
                string_msg = 'You are not authorized to access to this page.'
                messages.add_message(self.request, messages.ERROR, string_msg)
                referer = request.META.get('HTTP_REFERER', '/')
                return redirect(referer)
        else:
            return redirect_to_login(
                request.get_full_path(),
                self.get_login_url(),
                self.get_redirect_field_name())

        return super(GroupRequiredMixin, self).dispatch(
            request, *args, **kwargs)
