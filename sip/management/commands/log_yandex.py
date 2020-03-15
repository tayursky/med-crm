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
from utils.clean_data import get_numbers


class Command(BaseCommand):
    help = 'fix log yandex'

    def handle(self, *args, **options):
        count = 0
        for item in Log.objects.filter(event_type='web_hook'):
            count += 1
            item.event_type = item.data.get('EventType')
            item.entry_id = item.data.get('Body', {}).get('Id')
            item.from_number = item.data.get('Body', {}).get('From').replace('+', '')
            item.to_number = item.data.get('Body', {}).get('To').replace('+', '')

            if item.data.get('Timestamp'):
                item.entry_datetime = datetime.strptime(item.data.get('Timestamp')[:-2], '%Y-%m-%dT%H:%M:%S.%f')
            item.save()
            print(item.event_type)

        for item in Log.objects.filter(entry_datetime=None):
            count += 1
            print(item.event_type, count)
            item.entry_datetime = item.created_at
            item.save()

        print('count', count)
