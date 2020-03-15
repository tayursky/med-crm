# -*- coding: utf-8 -*-

from datetime import date, datetime, timedelta

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from deal.models import Deal, DealTask
from identity.models import Person, PersonPhone


class Command(BaseCommand):
    help = 'fix deals'

    def handle(self, *args, **options):
        print('Begin update cache \n')

        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        # models = ['deal', 'person', 'phone']
        # if options['model']:
        #     models = [options['model']]

        cnt = 0
        for person in Person.objects.filter(cache__pravka=1).exclude(rel_deals__control=True):
            cnt += 1
            print('person',
                  person.cache['pravka'],
                  person.id,
                  person.rel_deals.all()[0].deal.start_datetime
                  )
            try:
                start_datetime = person.rel_deals \
                    .filter(control=False, deal__step__name='done').first().deal.start_datetime
            except AttributeError:
                start_datetime = today

            for key in ['ask_result', 'to_control']:
                task, _ = DealTask.objects.get_or_create(
                    type=key,
                    client=person,
                    title=settings.TASK_TYPE_SET[key]['title'],
                    time_planned=start_datetime + timedelta(days=settings.TASK_TYPE_SET[key]['days'])
                )
                print('A', start_datetime, task, _)

        print(cnt)

        # for deal in Deal.objects.all():
        #     print('deal', deal.id)
        #     deal.save()
        #
        # for phone in PersonPhone.objects.all():
        #     print('phone', phone.id)
        #     phone.save()

        print('\nEnd update cache')

    def add_arguments(self, parser):
        parser.add_argument(
            '-m',
            '--model',
            action='store_true',
            default=None,
            help='Имя модели'
        )
