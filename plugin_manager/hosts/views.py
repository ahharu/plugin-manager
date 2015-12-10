from django.contrib import messages
from django.core.urlresolvers import reverse_lazy, reverse
from django.http import JsonResponse
from django.views.generic import View
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
import requests
from django_tables2.views import RequestConfig, SingleTableView
from django.http import HttpResponseRedirect, HttpResponse
from django.conf import settings
from django.views.generic.edit import FormView
from django.template.response import TemplateResponse
from plugin_manager.core.mixins.views import MultipleGroupRequiredMixin, \
    GroupRequiredMixin
from plugin_manager.hosts import models, tables, forms
from plugin_manager.hosts.tables import HostPluginsInstalledTable
from plugin_manager.accounts.models import DeployUser, PermissionHost
from plugin_manager.hosts.forms import MembersAddForm
from plugin_manager.accounts.utils import \
    get_filtered_user_queryset_from_filter_dict
from plugin_manager.hosts.util import getAdvancedPermissionBlock
from jenkinsapi.jenkins import Jenkins
from bs4 import BeautifulSoup
from plugin_manager.hosts.tasks import update_plugin, delete_plugin, upload_plugin
from django.views.generic.detail import SingleObjectMixin
import uuid
import os

class HostMembersDelete(MultipleGroupRequiredMixin,
                        DeleteView):
    """
    Delete a project member
    """
    group_required = ('Admin', )
    model = PermissionHost
    template_name = 'hosts/host_members_confirm_delete.html'

    def get_object(self, queryset=None):
        return PermissionHost.objects.filter(user_id=self.kwargs['user_id'],
                                             host=self.kwargs[
                                                 'host_id']).first()
        """ Hook to ensure object is owned by request.user. """

    def get_success_url(self):
        return (reverse_lazy('hosts_host_members',
                             args=[self.kwargs['host_id']]))

    def post(self, request, *args, **kwargs):
        if "cancel" in request.POST:
            url = self.get_success_url()
            return HttpResponseRedirect(url)
        else:
            return super(HostMembersDelete, self).post(
                request, *args, **kwargs)


class HostMemberAdd(CreateView):
    """
    If it receives an action of add it adds member to project
    """

    def get(self, request, *args, **kwargs):
        hostid = kwargs.get('host_id')
        userid = request.GET.get('user_id')
        permhost = PermissionHost.objects.get_or_create(
            user=DeployUser.objects.get(pk=userid),
            host=models.Host.objects.get(pk=hostid))

        return HttpResponse()


class HostMembersAdd(MultipleGroupRequiredMixin,
                     CreateView):
    """
    Add a member to a host
    """
    group_required = ('Admin', )
    model = models.Host
    form_class = MembersAddForm
    template_name = 'hosts/host_members_add.html'
    formvalues = ['first_name', 'last_name', 'email', 'user_level']

    def get_success_url(self):
        return (reverse_lazy('hosts_host_members_add',
                             args=[self.kwargs['pk']]))

    def get_context_data(self, **kwargs):

        context = super(HostMembersAdd, self).get_context_data(**kwargs)
        context = {}
        users = ""

        context['pk'] = self.kwargs['pk']

        context['host'] = models.Host.objects.all().get(pk=context['pk'])

        context['form'] = MembersAddForm()

        first_name = self.request.GET.get(
            'first_name').strip() if self.request.GET.get(
            'first_name') else None
        last_name = self.request.GET.get(
            'last_name').strip() if self.request.GET.get(
            'last_name') else None
        email = self.request.GET.get(
            'email').strip() if self.request.GET.get(
            'email') else None
        user_level = self.request.GET.get(
            'user_level').strip() if self.request.GET.get(
            'user_level') else None

        context['form'].fields['first_name'].initial = first_name
        context['form'].fields['last_name'].initial = last_name
        context['form'].fields['email'].initial = email
        context['form'].fields['user_level'].initial = user_level

        fields = ['first_name', 'last_name', 'email', 'user_level']
        filterdict = {}
        for field in fields:
            if context['form'].fields[field].initial is not None:
                filterdict[field] = context['form'].fields[field].initial
        if (len(filterdict) != 0):
            users = get_filtered_user_queryset_from_filter_dict(
                filterdict).exclude(
                pk__in=PermissionHost.objects.filter(host=context[
                    'host']).values_list('user'))
        else:
            users = DeployUser.active_records.all()

        context['members'] = users

        members_table = tables.HostMembersAddTable(users, prefix='members_')

        RequestConfig(self.request, paginate={"per_page": getattr(settings,
                                                                  "NUM_RESULTS_PER_PAGE",
                                                                  None)}).configure(
            members_table)
        context['members_table'] = members_table
        if (first_name or last_name or email or user_level) and \
                (users.count() != 0):
            context['show_table'] = True
        else:
            context['show_table'] = False

        return context


class HostMembersList(MultipleGroupRequiredMixin,
                      DetailView):
    """
    Update a project members
    """
    group_required = ('Admin', )
    model = models.Host
    template_name = 'hosts/host_members.html'

    def get_context_data(self, **kwargs):
        context = super(HostMembersList, self).get_context_data(**kwargs)

        users = DeployUser.objects.filter(
            pk__in=PermissionHost.objects.filter(host=kwargs[
                'object']).values_list(
            'user'))
        context['members'] = users

        members_table = tables.HostMembersTable(users, prefix='members_',
                                                host_id=self.kwargs['pk'])
        RequestConfig(self.request, paginate={"per_page": getattr(
            settings, "NUM_RESULTS_PER_PAGE", None)}).configure(
            members_table)
        context['members_table'] = members_table

        return context


class HostList(MultipleGroupRequiredMixin, SingleTableView):
    group_required = ['Admin', 'Deployer', ]
    table_class = tables.HostTable
    model = models.Host
    table_pagination = {
    "per_page": getattr(settings, "NUM_RESULTS_PER_PAGE", None)}


class HostDetail(MultipleGroupRequiredMixin, DetailView):
    group_required = ['Admin', 'Deployer', ]
    model = models.Host

    def get_url(self,name,list):
        if name in list:
            return 'hosts_host_plugin_update'
        else:
            return 'hosts_host_plugin_upload_wn'

    def get_context_data(self, **kwargs):
        context = super(HostDetail, self).get_context_data(**kwargs)

        host = self.get_object()
        context['pk'] = self.kwargs['pk']
        jenkins_server = Jenkins('http://'+host.name,host.jenkins_username,host.jenkins_password)

        ## Get Current Available Plugins
        html_plugins = 'http://updates.jenkins-ci.org/download/plugins/'
        html_doc = requests.get(html_plugins)
        soup = BeautifulSoup(html_doc.text, 'html.parser')
        asfind = soup.find_all('a')
        asfind = asfind[5:]
        plugins = [x.string.strip("/") for x in asfind]
        installed_plugins = jenkins_server.get_plugins().values()
        plugin_list = [{'name':x.shortName,'version':x.version,'url':self.get_url(x.shortName,plugins)} for x in installed_plugins]
        sorted_plugin_list = sorted(plugin_list, key=lambda k: k['name'])
        context['plugin'] = sorted_plugin_list
        table = HostPluginsInstalledTable(sorted_plugin_list,
                                          host_id=self.kwargs['pk'])

        RequestConfig(self.request, paginate={"per_page": getattr(
            settings, "NUM_RESULTS_PER_PAGE", None)}).configure(
            table)
        context['table'] = table
        return context

class HostPluginUpdate(FormView):
    model = models.Host
    permission_required = ['hosts.change_host']
    form_class = forms.HostPluginUpdateForm
    template_name_suffix = '_update_plugin'
    template_name = 'hosts/host_update_plugin.html'

    def get_form_kwargs(self):
        kwargs = {}
        html_plugins = 'http://updates.jenkins-ci.org/download/plugins/%s' % self.kwargs['plugin_name']
        html_doc = requests.get(html_plugins)
        soup = BeautifulSoup(html_doc.text, 'html.parser')
        asfind = soup.find_all('a')
        versions = [x.string for x in asfind if x.string!='permalink to the latest']
        initial = super(HostPluginUpdate, self).get_initial()

        kwargs['versions'] = versions
        return kwargs

    def get_initial(self):
        """
        Returns the initial data to use for forms on this view.
        """

        html_plugins = 'http://updates.jenkins-ci.org/download/plugins/%s' % self.kwargs['plugin_name']
        html_doc = requests.get(html_plugins)
        soup = BeautifulSoup(html_doc.text, 'html.parser')
        asfind = soup.find_all('a')
        versions = [x.string for x in asfind if x.string!='permalink to the latest']

        initial = super(HostPluginUpdate, self).get_initial()
        initial['versions'] = versions
        print("getting initials!")
        print(initial['versions'])

        return initial


    def get_context_data(self, **kwargs):
        context = super(HostPluginUpdate, self).get_context_data(**kwargs)
        context['plugin_name'] = self.kwargs['plugin_name']
        context['host_name'] = models.Host.objects.get(pk=self.kwargs['pk'])

        return context

    def dispatch(self, request, *args, **kwargs):
        self.host_id = kwargs.get('pk')

        host = models.Host.objects.get(pk=self.host_id)

        instance = host

        redirect = getAdvancedPermissionBlock(self.request,
                                              self.permission_required,
                                              instance)
        if redirect:
            return redirect
        else:
            return super(HostPluginUpdate, self).dispatch(
                request, *args, **kwargs)


    def form_invalid(self, form):
        myform = forms.HostPluginUpdateForm(self.request.POST)
        form_valid_from_parent = self.form_valid(form)
        if self.form_valid(form):
            form_valid_from_parent = self.get_success_url()
            host = models.Host.objects.get(pk=self.host_id)
            showname = myform.data['plugin_name'] if myform.data['plugin_name'] != '' else self.request.FILES['file'].name
            update_plugin.delay(host=host,
                                username=host.ssh_username,
                                password=host.ssh_password,
                                jenkins_username=host.jenkins_username,
                                jenkins_password=host.jenkins_password,
                                plugin_name=showname,
                                plugin_version=myform.data['versions'])
            msg = 'Plugin {} on Host {} Successfully Updated'.format(self.kwargs['plugin_name'],host)
            messages.success(self.request, msg)
            return HttpResponseRedirect(form_valid_from_parent)
        else:
            return None

    def form_valid(self, form):
        """First call the parent's form valid then let the user know it worked.
        """
        form_valid_from_parent = self.get_success_url()
        host = models.Host.objects.get(pk=self.host_id)
        return form_valid_from_parent

    def get_success_url(self):
        """"""
        return reverse('hosts_host_detail', kwargs={'pk': self.kwargs['pk']})

class HostPluginInstall(FormView):
    model = models.Host
    permission_required = ['hosts.change_host']
    form_class = forms.HostPluginInstallForm
    template_name_suffix = '_install_plugin'
    template_name = 'hosts/host_install_plugin.html'

    def get_form_kwargs(self):
        kwargs = {}
        html_plugins = 'http://updates.jenkins-ci.org/download/plugins/'
        html_doc = requests.get(html_plugins)
        soup = BeautifulSoup(html_doc.text, 'html.parser')
        asfind = soup.find_all('a')
        asfind = asfind[5:]
        plugins = [x.string.strip("/") for x in asfind]

        initial = super(HostPluginInstall, self).get_initial()

        kwargs['plugins'] = plugins
        return kwargs


    def get_context_data(self, **kwargs):
        context = super(HostPluginInstall, self).get_context_data(**kwargs)
        #context['plugin_name'] = self.kwargs['plugin_name']
        context['host_name'] = models.Host.objects.get(pk=self.kwargs['pk'])

        return context

    def dispatch(self, request, *args, **kwargs):
        self.host_id = kwargs.get('pk')

        host = models.Host.objects.get(pk=self.host_id)

        instance = host

        redirect = getAdvancedPermissionBlock(self.request,
                                              self.permission_required,
                                              instance)
        if redirect:
            return redirect
        else:
            return super(HostPluginInstall, self).dispatch(
                request, *args, **kwargs)


    def form_invalid(self, form):
        myform = forms.HostPluginInstallForm(self.request.POST)
        form_valid_from_parent = self.form_valid(form)
        if self.form_valid(form):
            form_valid_from_parent = self.get_success_url()
            host = models.Host.objects.get(pk=self.host_id)
            update_plugin.delay(host=host,
                                 username=host.ssh_username,
                                 password=host.ssh_password,
                                 jenkins_username=host.jenkins_username,
                                 jenkins_password=host.jenkins_password,
                                 plugin_name=myform.data['plugins'],
                                 plugin_version=myform.data['versions'])
            msg = 'Plugin {} on Host {} Successfully Updated'.format(myform.data['plugins'],host)
            messages.success(self.request, msg)
            return HttpResponseRedirect(form_valid_from_parent)
        else:
            return None

    def form_valid(self, form):
        """First call the parent's form valid then let the user know it worked.
        """
        form_valid_from_parent = self.get_success_url()
        host = models.Host.objects.get(pk=self.host_id)
        return form_valid_from_parent

    def get_success_url(self):
        """"""
        return reverse('hosts_host_detail', kwargs={'pk': self.kwargs['pk']})


class HostPluginDelete(DeleteView):
    model = models.Plugin
    permission_required = ['hosts.change_host']
    template_name = 'hosts/plugin_confirm_delete.html'

    def get_object(self, queryset=None):
        myplugin = models.Plugin()
        myplugin.name =self.kwargs['plugin_name']
        myplugin.version = 'todelete'

        return myplugin

    def get_success_url(self):
        """"""
        return reverse('hosts_host_detail', kwargs={'pk': self.kwargs['pk']})

    def delete(self, request, *args, **kwargs):
        host = models.Host.objects.get(pk=self.kwargs['pk'])

        ## Delete Logic here!

        delete_plugin.delay(host=host,
                            username=host.ssh_username,
                            password=host.ssh_password,
                            jenkins_username=host.jenkins_username,
                            jenkins_password=host.jenkins_password,
                            plugin_name=self.kwargs['plugin_name'],)

        msg = 'Plugin {} on Host {} Successfully Deleted'.format(self.kwargs['plugin_name'],host)
        messages.success(self.request, msg)
        url =  reverse('hosts_host_detail', kwargs={'pk': self.kwargs['pk']})
        return HttpResponseRedirect(url)

class HostCreate(CreateView):
    """View for creating a host. Hosts let us know where we can shovel code to.
    """
    model = models.Host
    form_class = forms.HostCreateForm
    template_name_suffix = '_create'

    permission_required = ['hosts.add_host']

    def dispatch(self, request, *args, **kwargs):

        redirect = getAdvancedPermissionBlock(self.request,
                                              self.permission_required,
                                              None)
        if redirect:
            return redirect
        else:
            return super(HostCreate, self).dispatch(
                request, *args, **kwargs)


    def form_valid(self, form):
        """First call the parent's form valid then let the user know it worked."""
        form_valid_from_parent = super(HostCreate, self).form_valid(form)
        messages.success(self.request, 'Host {} Successfully Created'.format(self.object))
        newph = PermissionHost(user=self.request.user, host=self.object)
        newph.save()
        return form_valid_from_parent

    def get_success_url(self):
        """Send them back to the detail view for that host"""
        return reverse('hosts_host_detail', kwargs={'pk': self.object.pk})


class HostUpdate(UpdateView):

    model = models.Host
    form_class = forms.HostUpdateForm
    template_name_suffix = '_update'

    permission_required = ['hosts.change_host']

    def dispatch(self, request, *args, **kwargs):
        self.host_id = kwargs.get('pk')

        host = models.Host.objects.get(pk=self.host_id)

        instance = host

        redirect = getAdvancedPermissionBlock(self.request,
                                              self.permission_required,
                                              instance)
        if redirect:
            return redirect
        else:
            return super(HostUpdate, self).dispatch(
                request, *args, **kwargs)

    def form_valid(self, form):
        """First call the parent's form valid then let the user know it worked.
        """

        form_valid_from_parent = super(HostUpdate, self).form_valid(form)
        msg = 'Host {} Successfully Updated'.format(self.object)
        messages.success(self.request, msg)

        return form_valid_from_parent

    def get_success_url(self):
        """"""
        return reverse('hosts_host_detail', kwargs={'pk': self.object.pk})


class HostDelete(GroupRequiredMixin, DeleteView):
    model = models.Host
    success_url = reverse_lazy('hosts_host_list')

    permission_required = ['hosts.delete_host']

    def dispatch(self, request, *args, **kwargs):
        self.host_id = kwargs.get('pk')

        host = models.Host.objects.get(pk=self.host_id)

        instance = host

        redirect = getAdvancedPermissionBlock(self.request,
                                              self.permission_required,
                                              instance)
        if redirect:
            return redirect
        else:
            return super(HostDelete, self).dispatch(
                request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        msg = 'Host {} Successfully Deleted'.format(self.get_object())
        messages.success(self.request, msg)
        return super(HostDelete, self).delete(self, request, *args, **kwargs)


class ProxyElasticSearch(View):
    def get(self, request):
        elk_url = settings.ELK_URL + ":" + settings.ELK_PORT
        response = requests.get(elk_url)

        return JsonResponse(response.json(), safe=False)


class GetVersionsByPluginNameAjax(SingleObjectMixin, View):

    def get(self, request, *args, **kwargs):
        if 'plugin_name' in kwargs:
            html_plugins = 'http://updates.jenkins-ci.org/download/plugins/%s' % kwargs.get('plugin_name')
            html_doc = requests.get(html_plugins)
            soup = BeautifulSoup(html_doc.text, 'html.parser')
            asfind = soup.find_all('a')
            versions = [x.string for x in asfind if x.string!='permalink to the latest']

            return JsonResponse([{'version': o, } for o in versions],
                                safe=False)
        else:
            return JsonResponse({'error': "No Ajax"})


class HostPluginUpload(FormView):
    model = models.Host
    permission_required = ['hosts.change_host']
    form_class = forms.UploadFileForm
    template_name_suffix = '_install_plugin'
    template_name = 'hosts/host_install_plugin.html'

    def get_form_kwargs(self):
        kwargs = {}
        return kwargs


    def get_context_data(self, **kwargs):
        context = super(HostPluginUpload, self).get_context_data(**kwargs)
        #context['plugin_name'] = self.kwargs['plugin_name']
        context['host_name'] = models.Host.objects.get(pk=self.kwargs['pk'])

        return context

    def dispatch(self, request, *args, **kwargs):
        self.host_id = kwargs.get('pk')

        host = models.Host.objects.get(pk=self.host_id)

        instance = host

        redirect = getAdvancedPermissionBlock(self.request,
                                              self.permission_required,
                                              instance)
        if redirect:
            return redirect
        else:
            return super(HostPluginUpload, self).dispatch(
                request, *args, **kwargs)


    def form_invalid(self, form):
        myform = forms.HostPluginInstallForm(self.request.POST)
        form_valid_from_parent = self.form_valid(form)
        if self.form_valid(form):
            form_valid_from_parent = self.get_success_url()
            host = models.Host.objects.get(pk=self.host_id)
            f = self.request.FILES['file']
            unique_fname = uuid.uuid4()
            os.mkdir('/tmp/%s' % unique_fname)
            path = '/tmp/%s/%s' % (unique_fname,self.request.FILES['file'].name)

            with open('/tmp/%s/%s' % (unique_fname,self.request.FILES['file'].name)
                        , 'wb+') as destination:
                    for chunk in f.chunks():
                        destination.write(chunk)
            showname = myform.data['plugin_name'] if myform.data['plugin_name'] != '' else self.request.FILES['file'].name
            upload_plugin.delay(host=host,
                                username=host.ssh_username,
                                password=host.ssh_password,
                                 jenkins_username=host.jenkins_username,
                                 jenkins_password=host.jenkins_password,
                                 plugin_name=myform.data['plugin_name'],
                                 file_path=path)
            msg = 'Plugin {} on Host {} Successfully Uploaded'.format(showname,host)
            messages.success(self.request, msg)
            return HttpResponseRedirect(form_valid_from_parent)
        else:
            return None

    def form_valid(self, form):
        """First call the parent's form valid then let the user know it worked.
        """
        form_valid_from_parent = self.get_success_url()
        host = models.Host.objects.get(pk=self.host_id)
        return form_valid_from_parent

    def get_success_url(self):
        """"""
        return reverse('hosts_host_detail', kwargs={'pk': self.kwargs['pk']})


class HostPluginUploadWithName(FormView):
    model = models.Host
    permission_required = ['hosts.change_host']
    form_class = forms.UploadFileFormWithName
    template_name_suffix = '_install_plugin_with_name'
    template_name = 'hosts/host_install_plugin_with_name.html'

    def getFileNameWithoutExtension(self,path):
        return path.split('\\').pop().split('/').pop().rsplit('.', 1)[0]

    def get_form_kwargs(self):
        kwargs = {}
        return kwargs


    def get_context_data(self, **kwargs):
        context = super(HostPluginUploadWithName, self).get_context_data(**kwargs)
        context['plugin_name'] = self.kwargs['plugin_name']
        context['host_name'] = models.Host.objects.get(pk=self.kwargs['pk'])

        return context

    def dispatch(self, request, *args, **kwargs):
        self.host_id = kwargs.get('pk')

        host = models.Host.objects.get(pk=self.host_id)

        instance = host

        redirect = getAdvancedPermissionBlock(self.request,
                                              self.permission_required,
                                              instance)
        if redirect:
            return redirect
        else:
            return super(HostPluginUploadWithName, self).dispatch(
                request, *args, **kwargs)


    def form_invalid(self, form):
        myform = forms.UploadFileFormWithName(self.request.POST)
        form_valid_from_parent = self.form_valid(form)
        if self.form_valid(form):
            form_valid_from_parent = self.get_success_url()
            host = models.Host.objects.get(pk=self.host_id)
            f = self.request.FILES['file']
            unique_fname = uuid.uuid4()
            os.mkdir('/tmp/%s' % unique_fname)
            path = '/tmp/%s/%s' % (unique_fname,self.request.FILES['file'].name)

            with open('/tmp/%s/%s' % (unique_fname,self.request.FILES['file'].name)
                        , 'wb+') as destination:
                    for chunk in f.chunks():
                        destination.write(chunk)
            showname = self.request.FILES['file'].name
            upload_plugin.delay(host=host,
                                username=host.ssh_username,
                                password=host.ssh_password,
                                 jenkins_username=host.jenkins_username,
                                 jenkins_password=host.jenkins_password,
                                 plugin_name=self.getFileNameWithoutExtension(showname),
                                 file_path=path)
            msg = 'Plugin {} on Host {} Successfully Uploaded'.format(showname,host)
            messages.success(self.request, msg)
            return HttpResponseRedirect(form_valid_from_parent)
        else:
            return None

    def form_valid(self, form):
        """First call the parent's form valid then let the user know it worked.
        """
        form_valid_from_parent = self.get_success_url()
        host = models.Host.objects.get(pk=self.host_id)
        return form_valid_from_parent

    def get_success_url(self):
        """"""
        return reverse('hosts_host_detail', kwargs={'pk': self.kwargs['pk']})