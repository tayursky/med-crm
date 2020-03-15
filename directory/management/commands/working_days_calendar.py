# -*- coding: utf-8 -*-

from datetime import date, datetime
import requests

from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import ugettext as _

from directory.models import WorkingDaysCalendar


class Command(BaseCommand):
    help = 'calendar parse'

    def handle(self, *args, **options):
        print('\nStart calendar_parse\n')

        WorkingDaysCalendar.calendar_parse(2019)

        print('\nFinish')
