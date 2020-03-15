# -*- coding: utf-8 -*-

from datetime import date, datetime, timedelta
import requests

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import ugettext as _
from deal.models import DealPerson
from sms.models import Sms
from sms.views.sms import deal_remind_1day
from utils.clean_data import get_numbers

SMS_TEST = settings.SMS_TEST


class Command(BaseCommand):
    help = 'sms send'

    def handle(self, *args, **options):
        api_id = '1F7A19AE-9F45-C080-89AD-28B3A2AD1632'
        print('\nStart sms send\n')

        deal_remind_1day()
        now = datetime.now().replace(minute=0, microsecond=0)

        for sms in Sms.objects.filter(status='wait'):
            timezone = sms.deal.branch.city.timezone if sms.deal else 0
            local_time = now + timedelta(hours=timezone)

            if sms.phone:
                phone = sms.phone
            else:
                phone = str(sms.person.phones.first())
            phone = get_numbers(phone)

            print('\n', sms.id, phone, sms)
            if not 9 <= local_time.hour < 20:  # СМС отправляем только в рабочие часы
                print('Ждем рабочие часы: 8-20', now, local_time)
                continue

            string = 'https://sms.ru/sms/send'
            params = dict(
                api_id=api_id,
                to=phone,
                msg=sms.text,
                json=1
            )
            if SMS_TEST:
                params['test'] = 1
            response = requests.get(url=string, params=params).json()

            if response['status'] == 'OK' and response['sms'][phone]['status']:
                sms.time_sent = datetime.now()
                sms.phone = phone
                try:
                    sms.status_text = response['sms'][phone]['status_text']
                except KeyError:
                    pass
                if response['sms'][phone]['status'] == 'ERROR':
                    sms.status = 'error'
                elif response['sms'][phone]['status'] == 'OK':
                    sms.status = 'ok'
                sms.save()
                if sms.deal:
                    sms.deal.sms_processed(sms, response)

        print('\nFinish sms send')
