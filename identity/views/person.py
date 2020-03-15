from decimal import Decimal
from django.core import serializers
from django.db.models import Avg, Sum
from django.urls import reverse, reverse_lazy
from django.http import HttpResponse, JsonResponse
from django.views.generic import DetailView, ListView, TemplateView, View
from django.shortcuts import render, render_to_response, get_object_or_404, redirect, reverse
from django.forms.models import modelform_factory
from django.contrib.auth.views import LoginView

from django.contrib.auth.mixins import LoginRequiredMixin

from mlm.forms import AgentCabinetForm
from identity.models import Account, Person
from utils.normalize_data import normalise_phone


class PersonSearchView(View):
    model = Person
    full_name, last_name, first_name, patronymic = None, None, None, None
    phone = None

    def dispatch(self, request, *args, **kwargs):
        self.full_name = request.GET.get('full_name', '').strip().split(' ')
        self.last_name = self.full_name[0] if len(self.full_name) > 0 else None
        self.first_name = self.full_name[1] if len(self.full_name) > 1 else None
        self.patronymic = self.full_name[2] if len(self.full_name) > 2 else None
        self.phone = normalise_phone(request.GET.get('phone'))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        person_qs = Person.objects.all()
        if self.last_name:
            person_qs = person_qs.filter(last_name__istartswith=self.last_name)
        if self.first_name:
            person_qs = person_qs.filter(first_name__istartswith=self.first_name)
        if self.patronymic:
            person_qs = person_qs.filter(patronymic__istartswith=self.patronymic)
        if self.phone:
            person_qs = person_qs.filter(phones__value__contains=self.phone)
        items = []
        for person in person_qs[:7]:
            items.append(dict(
                id=person.id,
                birthday=person.birthday.strftime('%d.%m.%Y') if person.birthday else None,
                caсhe=person.cache,
            ))
        context = dict(
            items=items
        )
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()

        if self.request.GET.get('debug'):
            return render_to_response('debug.jinja2', locals())
        return JsonResponse(context)
