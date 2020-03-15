# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from company.models import Branch
from directory.models import City


class Command(BaseCommand):
    help = 'fix deals'

    def handle(self, *args, **options):
        print('Begin check for deals\n')

        for city in City.objects.all():
            if not city.branch_set.all():
                Branch.objects.create(city=city, name='основной')
                print('no branch', city)


        print('End check')
