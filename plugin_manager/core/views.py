import json
from datetime import timedelta, datetime

from django.db import connection
from django.db.models.aggregates import Count
from django.contrib import messages
from django.utils.timezone import now
from django.views.generic import TemplateView
from django.template.defaultfilters import date as format_date
from django.template.defaultfilters import time as format_time
from croniter import croniter

from plugin_manager.launch_window.models import LaunchWindow


class Dashboard(TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):

        context = super(Dashboard, self).get_context_data(**kwargs)

        context['chart_data'] = ""

        return context
