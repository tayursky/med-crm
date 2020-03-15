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


class CalculateView(LoginRequiredMixin, View):
    model = Agent
    agent = None
    cost = 0
    permissions = []

    def dispatch(self, request, *args, **kwargs):
        try:
            self.agent = self.model.objects.get(pk=request.GET.get('agent'))
        except (ValueError, TypeError, Agent.DoesNotExist):
            pass
        self.cost = Decimal(request.GET.get('cost') or '0.00')
        self.permissions = self.model.get_permissions(request)
        return super().dispatch(request, *args, **kwargs)

    def get_cost(self):
        if self.agent:
            cost = Decimal(self.cost - (self.cost / 100 * self.agent.discount))
            return round(cost, 2)
        return self.cost

    def get(self, request, *args, **kwargs):
        context = dict(
            cost=self.get_cost()
        )
        return JsonResponse(context, safe=False)
