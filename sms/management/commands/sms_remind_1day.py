# -*- coding: utf-8 -*-

from datetime import date, datetime
import requests

from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import ugettext as _
from deal.models import DealPerson
from sms.models import Sms
from sms.views.sms import deal_remind_1day


class Command(BaseCommand):
    help = 'sms send'

    def handle(self, *args, **options):
        print('\nStart deal_remind_1day\n')

        deal_remind_1day()

        print('\nFinish')
