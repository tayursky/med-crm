# -*- coding: utf-8 -*-

from datetime import date, datetime, timedelta
import requests

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import ugettext as _

from utils.clean_data import get_numbers
from deal.models import Deal
from sms.models import Sms, SmsTemplate
from sms.views.sms import deal_remind_1day


class Command(BaseCommand):
    help = 'sms spam'

    def handle(self, *args, **options):
        template_q = SmsTemplate.objects.get(name='2020-03')
        count = 0
        list_related = getattr(Deal, 'list_related', [])
        queryset = Deal.objects \
            .filter(branch__city__name='Москва', stage__name='cancel') \
            .select_related(*list_related) \
            .order_by('start_datetime')

        for deal in queryset.all():
            print('\n', deal.id, deal.start_datetime)
            for person in deal.persons.all():
                try:
                    phone = get_numbers(person.phones.first())
                except:
                    continue

                if phone and (phone[0] == '7' and len(phone) == 11):
                    print(phone)
                else:
                    print('no!', phone, len(phone))
                    continue

                if Sms.objects.filter(phone=phone, template=template_q).exists():
                    print('exists')
                    continue

                Sms.objects.create(
                    deal=deal,
                    person=person,
                    phone=phone,
                    text=template_q.template,
                    template=template_q
                )
                count += 1

            if count == 1000:
                break

        print('\nFinish sms spam')
        print('count:', count)
