# -*- coding: utf-8 -*-

from datetime import date, datetime, timedelta
import json
import requests
import hashlib

from django.urls import reverse, reverse_lazy
from django.db.models import Q, Count, Max, Min
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import DetailView, ListView, TemplateView, View
from django.forms import models as model_forms
from django.views.decorators.csrf import csrf_exempt

from absolutum.settings import MANGO_API_KEY, MANGO_API_SALT
from directory.utils import get_model, get_linked_obj, get_detail_fields_mapping, get_child_list
from identity.models import Person
from sip.models import Log
from utils.clean_data import get_numbers


class SipLog(View):
    """
        Фиксация событий
    """
    model = Log
    phone = None  # Номер звонящего
    sip_id = None
    event = None

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        self.event = kwargs.get('event')
        return super(SipLog, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        print('Events')
        return JsonResponse(dict(message='ok'), safe=False)

    def post(self, request, *args, **kwargs):
        _json = request.POST.get('json')
        sign = request.POST.get('sign')
        vpbx_api_key = request.POST.get('vpbx_api_key')
        if not check_sign(vpbx_api_key, sign, _json):
            return JsonResponse(dict(error='wrong key'), safe=False)

        data = json.loads(_json)
        log = Log.objects.create(
            event_type=self.event,
            from_number=data.get('from', {}).get('number').replace('+', ''),
            to_number=data.get('to', {}).get('number').replace('+', ''),
            data=data
        )
        print('Event', log.id)
        return JsonResponse(dict(message='ok'), safe=False)


class GetIncoming(View):
    """
        Берем последние входящие звонки
    """
    model = Log
    sip_id = None  # Персональный sip_id
    limit = 0
    timezone = 0

    def dispatch(self, request, *args, **kwargs):
        self.sip_id = self.request.user.person.sip_id
        try:
            self.limit = int(request.GET.get('limit'))
        except ValueError:
            self.limit = 1
        self.timezone = request.user.person.timezone
        return super(GetIncoming, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        calls = []
        # , to_number='sip:%s' % self.request.user.person.sip_id) \
        log_qs = Log.objects \
            .filter(event_type__icontains='IncomingCall') \
            .values('from_number') \
            .annotate(Max('entry_datetime')) \
            .order_by('-entry_datetime__max')

        for item in log_qs[:self.limit]:
            person = Person.objects.filter(phones__value=item['from_number']).values('id', 'cache')
            persons = [p for p in person]
            calls.append(dict(
                time=(item['entry_datetime__max'] + timedelta(hours=self.timezone)).strftime('%d %H:%M:%S'),
                phone=item['from_number'],
                persons=persons
            ))

        calls_sorted = []
        content = dict(
            calls=calls
        )
        return JsonResponse(content, safe=False)


def check_sign(vpbx_api_key, sign, _json):
    sign_txt = '%s%s%s' % (MANGO_API_KEY, _json, MANGO_API_SALT)
    _sign = hashlib.sha256(str(sign_txt).encode('utf-8')).hexdigest()
    return vpbx_api_key == MANGO_API_KEY and sign == _sign
