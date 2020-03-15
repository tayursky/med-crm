# -*- coding: utf-8 -*-

from datetime import date, datetime, timedelta
from django.core.management.base import BaseCommand, CommandError

from absolutum.settings import DATETIME_FORMAT
from deal.models import Deal, DealTask


class Command(BaseCommand):
    help = 'fix deals'

    def handle(self, *args, **options):
        print('Begin fix for deal.steps\n')

        cnt = 0
        for deal in Deal.objects.all():  # .filter(id=1502):
            cnt += 1
            status = deal.status
            if status == 'reject':
                deal.step = deal.service.template.steps.get(name='cancel')
                # import ipdb; ipdb.set_trace()
                # break
            elif status == 'ok':
                deal.step = deal.service.template.steps.get(name='done')
            print(deal)
            deal.save()

        print('count', cnt)
        print('End fix')
