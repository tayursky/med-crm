# -*- coding: utf-8 -*-

from django.urls import reverse, reverse_lazy
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import ListView, TemplateView
from django.forms import models as model_forms

from directory.utils import get_model, get_linked_obj, get_detail_fields_mapping, get_child_list
from utils.remote_forms.forms import RemoteForm


class RemoteSearch(ListView):
    model = None
    query = None
    search_set = dict()

    def dispatch(self, request, *args, **kwargs):
        self.model = get_model(request.GET.get('model_name', kwargs.get('model_name')))
        self.search_set = getattr(self.model, 'search_set', dict())
        self.query = request.GET.get('query', None)
        return super(RemoteSearch, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        q = Q()
        for key, item in self.search_set.get('fields').items():

            kwargs = {item['key']: self.query}
            q |= Q(**kwargs)
        print(q)
        return self.model.objects.filter(q)[:28]

    def get(self, request, *args, **kwargs):
        items = []
        for i in self.get_queryset():
            label_display = getattr(i, 'get_label_display')
            items.append({
                'value': i.id,
                'label':  label_display() if label_display else i.__str__()
            })
        context = {
            'items': items
        }
        return JsonResponse(context, safe=False)
