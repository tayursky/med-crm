# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError

from company.models import Department
from deal.models import Expense, ExpenseType


class Command(BaseCommand):
    help = 'fix deals'

    def handle(self, *args, **options):
        print('Begin check for expenses\n')

        dep = Department.objects.filter(name='Правка').first()
        for item in ExpenseType.objects.all():
            print(item)
            item.departments.add(dep)
            item.save()

        print('\nEnd expenses')
