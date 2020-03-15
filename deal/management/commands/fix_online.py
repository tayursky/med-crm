# -*- coding: utf-8 -*-

from datetime import date, datetime, timedelta
from django.core.management.base import BaseCommand, CommandError

from absolutum.settings import DATETIME_FORMAT
from deal.models import Deal, DealTask


class Command(BaseCommand):
    help = 'fix deals'

    def handle(self, *args, **options):
        print('Begin fix for deals\n')

        cnt = 0
        for deal in Deal.objects.filter(comment__icontains='Онлайн', step__number__lt=3):
            cnt += 1
            print(deal, deal.cost)
            print(deal.comment, '\n')
            if not deal.cost:
                deal.cost = 15000
                deal.save()

        print('count', cnt)

        # for deal in Deal.objects.filter(service=10):
        #     if deal.start_datetime:
        #         deal.start_datetime -= timedelta(hours=1)
        #         deal.finish_datetime -= timedelta(hours=1)
        #         deal.save()
        #         print(deal.cache.get('title'))

        print('End fix')
