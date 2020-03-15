# -*- coding: utf-8 -*-

from datetime import date, datetime, timedelta
from django.core.management.base import BaseCommand, CommandError

from company.models import Branch
from deal.models import Deal


class Command(BaseCommand):
    help = 'fix deals'

    def handle(self, *args, **options):
        print('Begin move deals to center\n')

        new_branch = Branch.objects.get(name='Мед.центр')
        for deal in Deal.objects.filter(
                branch__name='Котельники',
                start_datetime__gte=datetime(2020, 2, 25),
        ).exclude(stage__label__in=['cancel', 'done']):
            print(deal)
            deal.branch = new_branch
            deal.save()
