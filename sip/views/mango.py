# -*- coding: utf-8 -*-

import json
import requests
import hashlib

from django.urls import reverse, reverse_lazy
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import View, DetailView, ListView, TemplateView
from django.forms import models as model_forms

from absolutum.settings import MANGO_ENABLE, MANGO_API_KEY, MANGO_API_SALT
from directory.utils import get_model, get_linked_obj, get_detail_fields_mapping, get_child_list
from sip.models import Log
from utils.clean_data import get_numbers


class MangoCall(View):
    """
        Инициализация исходящего звонка для Манго-офиса
    """
    model = Log
    phone = None  # Вызываемый номер
    sip_id = None  # Персональный sip_id
    sip_extension = 101  # внутренний номер, за счет которого производится звонок (например 101)
    sip_url = 'https://app.mango-office.ru/vpbx/commands/callback'

    def dispatch(self, request, *args, **kwargs):
        self.sip_id = self.request.user.person.sip_id
        self.phone = get_numbers(self.request.GET.get('phone'))
        return super(MangoCall, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if not self.sip_id:
            return JsonResponse(dict(
                message=dict(type='error', text='Не определен SIP идентификатор')
            ), safe=False)
        if not self.phone:
            return JsonResponse(dict(
                message=dict(type='error', text='Номер отсутствует')
            ), safe=False)

        log = Log.objects.create(
            event_type='crm_call',
            from_number='sip:%s' % self.sip_id,
            to_number=self.phone
        )
        _json = {
            'command_id': log.id,
            'from': dict(
                extension=self.sip_extension,
                number='sip:%s' % self.sip_id,
            ),
            'to_number': self.phone
        }
        json_encode = json.dumps(_json).replace(' ', '')
        sign_txt = '%s%s%s' % (MANGO_API_KEY, json_encode, MANGO_API_SALT)
        sign = hashlib.sha256(str(sign_txt).encode('utf-8')).hexdigest()
        data = dict(
            vpbx_api_key=MANGO_API_KEY,
            sign=sign,
            json=json_encode
        )
        r = requests.post(self.sip_url, data=data)
        log.data = dict(status_code=r.status_code, reason=r.reason)
        log.save()
        context = dict(
            message=dict(type='success',
                         text='Звонок на +%s' % self.phone)
        )
        return JsonResponse(context, safe=False)
