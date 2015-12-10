from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, ButtonHolder, Submit

from plugin_manager.hosts import models
from django.contrib.auth.models import Group


class HostCreateForm(forms.ModelForm):
    jenkins_password = forms.CharField(widget=forms.PasswordInput(), required=True)
    jenkins_username = forms.CharField( required=True)
    ssh_username = forms.CharField(required=True)
    ssh_password = forms.CharField(widget=forms.PasswordInput(), required=True)
    class Meta:
        model = models.Host
        fields = ['name', 'alias','ssh_username',
                  'ssh_password','jenkins_username','jenkins_password']

        widgets = {'ssh_password': forms.PasswordInput,
                    'jenkins_password': forms.PasswordInput}



    helper = FormHelper()
    helper.form_class = 'form-horizontal'
    helper.label_class = 'col-lg-2'
    helper.field_class = 'col-lg-8'
    helper.layout = Layout(
        'name',
        'alias',
        'ssh_username',
        'ssh_password',
        'jenkins_username',
        'jenkins_password',
        ButtonHolder(
            Submit('submit', 'Create Host', css_class='button')
        )
    )


    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'name',
            'alias',
            'ssh_username',
            'ssh_password',
            'jenkins_username',
            'jenkins_password',
            ButtonHolder(
                Submit('submit', 'Create Host', css_class='button')
            )
        )

        super(HostCreateForm, self).__init__(*args, **kwargs)

class HostUpdateForm(HostCreateForm):

    helper = FormHelper()
    helper.form_class = 'form-horizontal'
    helper.label_class = 'col-lg-2'
    helper.field_class = 'col-lg-8'
    helper.layout = Layout(
        'name',
        'alias',
        'ssh_username',
        'ssh_password',
        'jenkins_username',
        'jenkins_password',
        ButtonHolder(
            Submit('submit', 'Update Host', css_class='button')
        )
    )

class HostPluginUpdateForm(forms.Form):

    #name = forms.CharField(widget=forms.TextInput(attrs={'readonly':'readonly'}),required=True, label='Host Name')
    choices = []
    versions = forms.ChoiceField(required=True, label='Plugin Version to Install', initial=True,choices=choices)
    class Meta:
        #model = models.Host
        fields = ['versions']

        widgets = {}

    def __init__(self, *args, **kwargs):
        initial = kwargs.get('initial', {})
        instance = kwargs.get('instance', {})
        versions_kwarg = kwargs.pop('versions', None)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'versions',
        )
        self.helper.add_input(Submit('submit', 'Update', css_class='btn-default btn-sm pull-right'))

        self.helper.form_method = 'post'
        #kwargs.pop('instance', None)

        super(HostPluginUpdateForm, self).__init__(*args, **kwargs)
        choices= []
        self.choices = []
        if versions_kwarg:
            for choice in versions_kwarg:
                self.choices.append(
                    (choice, choice)
                )
        self.fields['versions'].choices = self.choices

class HostPluginInstallForm(forms.Form):

    #name = forms.CharField(widget=forms.TextInput(attrs={'readonly':'readonly'}),required=True, label='Host Name')
    choices = []
    versionchoices = []
    plugins = forms.ChoiceField(required=True, label='Plugin to Install', initial=True,choices=choices)
    versions = forms.ChoiceField(required=True, label='Version to Install', initial=True,choices=choices)
    class Meta:
        #model = models.Host
        fields = ['plugins','versions']

        widgets = {}

    def __init__(self, *args, **kwargs):
        initial = kwargs.get('initial', {})
        instance = kwargs.get('instance', {})
        plugins_kwarg = kwargs.pop('plugins', None)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'plugins',
            'versions',
        )
        self.helper.add_input(Submit('submit', 'Update', css_class='btn-default btn-sm pull-right'))

        self.helper.form_method = 'post'
        #kwargs.pop('instance', None)

        super(HostPluginInstallForm, self).__init__(*args, **kwargs)

        choices= []
        self.choices = []
        if plugins_kwarg:
            for choice in plugins_kwarg:
                self.choices.append(
                    (choice, choice)
                )
        self.fields['plugins'].choices = self.choices


class MembersAddForm(forms.Form):

    first_name = forms.CharField(label="First Name", required=False)
    last_name = forms.CharField(label="Last Name", required=False)
    email = forms.CharField(label="Email", required=False)
    user_level = forms.ModelChoiceField(Group.objects.all(),
                                        label="User Level",
                                        empty_label="Select...",
                                        required=False)

    def __init__(self, *args, **kwargs):

        self.helper = FormHelper()
        self.helper.layout = Layout(
            'first_name',
            'last_name',
            'email',
            'user_level',
        )
        self.helper.add_input(Submit('submit', 'Search', css_class='btn-default btn-sm pull-right'))

        self.helper.form_method = 'get'
        kwargs.pop('instance', None)

        super(MembersAddForm, self).__init__(*args, **kwargs)



class UploadFileForm(forms.Form):
    plugin_name = forms.CharField(max_length=50,required=False, label="Plugin Name ( if not defined we will use the filename )")
    file = forms.FileField(label="Plugin file",required=True)

    def __init__(self, *args, **kwargs):

            self.helper = FormHelper()
            self.helper.layout = Layout(
                'plugin_name',
                'file',
            )
            self.helper.add_input(Submit('submit', 'Install', css_class='btn-default btn-sm pull-right'))

            super(UploadFileForm, self).__init__(*args, **kwargs)

class UploadFileFormWithName(forms.Form):
    file = forms.FileField(label="Plugin file",required=True)

    def __init__(self, *args, **kwargs):

            self.helper = FormHelper()
            self.helper.layout = Layout(
                'plugin_name',
                'file',
            )
            self.helper.add_input(Submit('submit', 'Install', css_class='btn-default btn-sm pull-right'))

            super(UploadFileFormWithName, self).__init__(*args, **kwargs)