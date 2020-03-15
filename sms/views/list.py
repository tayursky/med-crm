import json
from datetime import date, datetime, timedelta

from django.apps import apps
from django.core import serializers
from django.urls import reverse, reverse_lazy
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from django.views.generic import DetailView, ListView, TemplateView, View
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin

from absolutum.settings import DATETIME_FORMAT
from deal.models import Client, Deal
from directory.utils import get_model, get_linked_obj, get_detail_fields_mapping, get_child_list
from mlm.models import Agent, Invite
from sms.models import Sms
from utils.choices import get_choices, filters_choices


class SmsList(LoginRequiredMixin, ListView):
    model = Sms
    client = None
    deal = None
    list_display = None
    count = 0
    permissions = []
    filters = {}
    timezone = 0

    def dispatch(self, request, *args, **kwargs):
        try:
            self.timezone = request.user.person.timezone
        except IndexError:
            pass
        try:
            self.client = Client.objects.get(pk=self.request.GET.get('client'))
        except Client.DoesNotExist:
            self.deal = Deal.objects.get(pk=self.request.GET.get('deal'))
        except Deal.DoesNotExist:
            pass
        self.permissions = self.model.get_permissions(request)
        self.permissions += Agent.get_permissions(request, full_label=True)
        self.list_display = ['id'] + getattr(self.model, 'list_display', [])
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        list_related = getattr(self.model, 'list_related', [])
        queryset = self.model.objects.none()

        if self.client:
            queryset = Sms.objects.filter(person=self.client)
        elif self.deal:
            queryset = self.deal.sms.all()

        queryset = queryset.select_related(*list_related).distinct()

        return queryset

    def get_items(self):
        items = []
        for item_q in self.get_queryset():
            item = dict(
                deal=item_q.deal_id,
                id=item_q.id,
                person=item_q.person_id,
                phone=item_q.phone,
                status=item_q.status,
                status_title=item_q.get_status_display(),
                text=item_q.text,
                time_created=(item_q.time_created + timedelta(hours=self.timezone)).strftime(DATETIME_FORMAT),
                time_sent=(item_q.time_sent + timedelta(hours=self.timezone)).strftime(DATETIME_FORMAT)
                if item_q.time_sent else ''
            )
            items.append(item)

        return items

    def get(self, request, *args, **kwargs):
        if not request.GET:
            return render(request, 'app_vue.jinja2')

        context = dict(
            title=self.model._meta.verbose_name_plural,
            meta_label=self.model._meta.label,
            model_name=self.model.__name__.lower(),
            url=self.request.path,
            headers=self.model.get_headers(),
            items=self.get_items(),
            count=self.count,
            permissions=self.permissions,
        )

        if request.GET.get('debug'):
            from django.shortcuts import render_to_response
            return render_to_response('debug.jinja2', locals())

        return JsonResponse(context)
