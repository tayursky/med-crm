# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
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
from django.http import HttpRequest

from absolutum.settings import MIGHTY_CALL_SET
from sip.models import Log, MightyCallUser
from utils.clean_data import get_numbers


class MightyCallWebHook(View):
    """
        MightyCall web hooks
    """
    data = dict()
    permissions = []

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        try:
            self.data = json.loads(request.body.decode('utf-8').replace('\r\n', '')),
        except json.decoder.JSONDecodeError:
            pass
        try:
            self.data = self.data[0]
        except IndexError:
            pass
        self.data.update(dict(
            remote_addr=request.META.get('REMOTE_ADDR')
        ))

        try:
            entry_datetime = datetime.strptime(self.data.get('Timestamp')[:-2], '%Y-%m-%dT%H:%M:%S.%f')
        except:
            entry_datetime = None

        Log.objects.create(
            event_type=self.data.get('EventType'),
            entry_id=self.data.get('Body', {}).get('Id'),
            from_number=self.data.get('Body', {}).get('From').replace('+', ''),
            to_number=self.data.get('Body', {}).get('To').replace('+', ''),
            entry_datetime=entry_datetime,
            data=self.data
        )
        return super(MightyCallWebHook, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        print('POST data', self.data)
        context = dict()

        if request.GET.get('debug'):
            from django.shortcuts import render_to_response
            return render_to_response('debug.jinja2', locals())
        return JsonResponse(context, safe=False)
