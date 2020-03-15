# -*- coding: utf-8 -*-

from datetime import date, datetime
import json
import random
import requests

from hashlib import sha256

from absolutum.settings import MANGO_API_KEY, MANGO_API_SALT
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import ugettext as _
from sip.models import Log


class Command(BaseCommand):
    help = 'sip'

    def handle(self, *args, **options):
        url = 'https://app.mango-office.ru/vpbx/commands/callback'  # commands/callback_group/
        sip_extension = 103  # внутренний номер, за счет которого производится звонок.(например 101)
        sip_id = 'user1@pravka.mangosip.ru'  # кто звонит(можно SIP)
        phone = 79951001108  # кому звонит

        log = Log.objects.create(
            event_type='crm_call',
            from_number='sip:%s' % sip_id,
            to_number=phone
        )
        _json = {
            'command_id': log.id,
            'from': dict(
                extension=sip_extension,
                number='sip:%s' % sip_id,
            ),
            'to_number': phone
        }
        json_encode = json.dumps(_json).replace(' ', '')
        sign_txt = '%s%s%s' % (MANGO_API_KEY, json_encode, MANGO_API_SALT)
        sign = sha256(str(sign_txt).encode('utf-8')).hexdigest()

        print('json_encode', json_encode)
        print('sign_txt', sign_txt)
        print('sign', sign)

        data = dict(
            vpbx_api_key=MANGO_API_KEY,
            sign=sign,
            json=json_encode
        )
        r = requests.post(url, data=data)

        print(r.status_code, r.reason, '\n')
        log.data = dict(status_code=r.status_code, reason=r.reason)
        log.save()

        # response = requests.get(string).json()
        # print(response.content)
        # print('\n', response)
