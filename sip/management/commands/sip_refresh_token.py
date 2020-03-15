# -*- coding: utf-8 -*-

from datetime import date, datetime
import json
import random
import requests
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from identity.models import Person
from sip.views.mighty_call import MightyCall
from sip.models import MightyCallUser

class Command(BaseCommand):
    help = 'sip refresh token'

    def handle(self, *args, **options):
        count = 0

        for mighty_user in MightyCallUser.objects.all():
            print(mighty_user)
            telephony = MightyCall(params=dict(mighty_user=mighty_user))
            telephony.get_user(refresh=True)

        print('count', count)
