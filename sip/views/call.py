# -*- coding: utf-8 -*-

import json
import requests
import hashlib

from django.urls import reverse, reverse_lazy
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View, DetailView, ListView, TemplateView
from django.forms import models as model_forms
from django.contrib.auth.mixins import LoginRequiredMixin

from sip.views.mighty_call import MightyCall
from utils.clean_data import get_numbers


class SipEvent(LoginRequiredMixin, View):
    """
        Инициализация исходящего звонка для MightyCall
    """
    event = None
    params = dict()
    permissions = []

    def dispatch(self, request, *args, **kwargs):
        self.event = kwargs.get('event')
        print('event', self.event)
        return super(SipEvent, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.params = self.request.GET.dict()
        self.params.update(
            person=self.request.user.person if self.request.user.person else None
        )
        print('GET params', self.params)
        telephony = MightyCall(params=self.params)
        try:
            answer, errors = getattr(telephony, self.event)()
        except AttributeError:
            answer, errors = None, dict(event='Нет такого метода (%s)' % self.event)

        if errors:
            return JsonResponse(dict(
                message=dict(type='error', errors=errors)
            ), safe=False)

        context = dict(
            answer=answer, errors=errors,
            message=dict(type='success', text='Звонок на +%s' % get_numbers(self.params.get('phone')))
        )

        if request.GET.get('debug'):
            from django.shortcuts import render_to_response
            return render_to_response('debug.jinja2', locals())
        return JsonResponse(context, safe=False)
