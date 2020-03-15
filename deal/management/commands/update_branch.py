# -*- coding: utf-8 -*-

from datetime import date, datetime, timedelta
from django.core.management.base import BaseCommand, CommandError

from company.models import Branch


class Command(BaseCommand):
    help = 'fix deals'

    def handle(self, *args, **options):
        print('Begin fix for task\n')

        cnt = 0
        for task in Branch.objects.all():
            task.save()
            print(task.id)
        print('count', cnt)

        print('End fix')
