from decimal import Decimal
import json
from django.core import serializers
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.urls import reverse, reverse_lazy
from django.http import HttpResponse, JsonResponse
from django.views.generic import DetailView, ListView, TemplateView, View
from django.shortcuts import render, get_object_or_404
from django.forms.models import modelform_factory

from mlm.models import Agent, Invite


class CheckView(LoginRequiredMixin, ListView):
    model = Agent
    query = None
    value = None
    permissions = []

    def dispatch(self, request, *args, **kwargs):
        self.value = request.GET.get('query')
        self.permissions = self.model.get_permissions(request)
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        print('self.value', self.value)
        queryset = self.model.objects.filter(
            Q(code__icontains=self.value) |
            Q(person__cache__full_name__icontains=self.value) |
            Q(person__phones__value__icontains=self.value)
        )
        return queryset.distinct()

    def get(self, request, *args, **kwargs):
        context = dict(
            items=[dict(label=i.__str__(), value=i.id) for i in self.get_queryset()]
        )
        return JsonResponse(context, safe=False)
