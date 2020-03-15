# -*- coding: utf-8 -*-

from datetime import date, datetime, timedelta
from django.core.management.base import BaseCommand, CommandError

from absolutum.settings import DATETIME_FORMAT
from company.models import User
from deal.models import Deal, DealTask


class Command(BaseCommand):
    help = 'fix deals'

    def handle(self, *args, **options):
        print('Begin fix for deal.steps\n')

        cnt = 0
        for deal in Deal.objects.filter(manager=None):
            cnt += 1
            for record in deal.history.all().order_by('history_date'):
                if record.history_user:
                    deal.manager = User.objects.get(account=record.history_user)
                    deal.save()
                    break
            if not deal.manager:
                print('fail', deal.id)

        print('count', cnt)
        print('End fix')
