import json
from datetime import date, datetime

from django.apps import apps
from django.core import serializers
from django.urls import reverse, reverse_lazy
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from django.views.generic import DetailView, ListView, TemplateView, View
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext as _

from directory.utils import get_model, get_linked_obj, get_detail_fields_mapping, get_child_list
from directory.models import WorkingDaysCalendar


class WorkingCalendarView(LoginRequiredMixin, View):
    model = WorkingDaysCalendar
    year = None
    month = None
    permissions = []

    def dispatch(self, request, *args, **kwargs):
        self.year = int(request.GET.get('year', date.today().year))
        self.month = request.GET.get('month')
        action = request.GET.get('action')
        if action == 'current':
            self.year = date.today().year
        elif action == 'next':
            self.year += 1
        elif action == 'prev':
            self.year -= 1
        elif action == 'parse':
            self.model.calendar_parse(self.year)
        print('year', self.year, 'month', self.month)

        self.permissions = self.model.get_permissions(request)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if 'view' not in self.permissions:
            return JsonResponse(dict(answer='No permissions'), safe=False)
        if not request.GET:
            return render(request, 'app_vue.jinja2')

        context = dict(
            title=self.model._meta.verbose_name_plural,
            meta_label=self.model._meta.label,
            model_name=self.model.__name__.lower(),
            url=self.request.path,
            calendar_set=self.model.get_calendar_set(year=self.year, month=self.month),
            permissions=self.permissions,
        )

        if request.GET.get('debug'):
            from django.shortcuts import render_to_response
            return render_to_response('debug.jinja2', locals())

        return JsonResponse(context)
