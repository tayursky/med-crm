# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError

from company.models import Branch, TimeTable
from deal.models import Deal
from identity.models import Person, PersonPhone
from mlm.models import Agent


class Command(BaseCommand):
    args = '<model_name ...>'
    help = 'Update cache'

    def add_arguments(self, parser):
        parser.add_argument('models', nargs='+', type=str)

    def handle(self, *args, **options):
        print('\nStart update cache')
        print('models', options['models'], '\n')

        models = options['models']
        if 'all' in options['models']:
            models = ['person', 'deal', 'phone', 'timetable', 'agent']

        if 'person' in models:
            for person in Person.objects.all():
                print('person', person.id)
                person.save()

        if 'phone' in models:
            for phone in PersonPhone.objects.all():
                print('phone', phone.id)
                phone.save()

        if 'deal' in models:
            for deal in Deal.objects.all():
                print('deal', deal.id)
                deal.save()

        if 'timetable' in models:
            for item in TimeTable.objects.all():
                print('timetable', item.id)
                item.save()

        if 'agent' in models:
            for item in Agent.objects.all():
                print('agent', item.id)
                item.save()

        if 'branch' in models:
            for item in Branch.objects.all():
                print('branch', item.id)
                item.save()

        print('\nEnd update cache\n')
