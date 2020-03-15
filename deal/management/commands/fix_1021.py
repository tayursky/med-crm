# -*- coding: utf-8 -*-

from datetime import date, datetime, timedelta
from django.core.management.base import BaseCommand, CommandError

from absolutum.settings import DATETIME_FORMAT
from deal.models import Deal, DealTask


class Command(BaseCommand):
    help = 'fix deals'

    def handle(self, *args, **options):
        print('Begin fix for task\n')

        cnt = 0
        for task in DealTask.objects.all():
            start = task.time_planned - timedelta(hours=12)
            end = start + timedelta(hours=12)
            # print('time_planned', task.time_planned.strftime(DATETIME_FORMAT),
            #       start.strftime(DATETIME_FORMAT),
            #       end.strftime(DATETIME_FORMAT))

            dub_list = DealTask.objects.filter(
                title=task.title, comment=task.comment, time_planned__gte=start, time_planned__lte=end,
                status='in_work'
            ).exclude(id=task.id)
            if task.client:
                dub_list = dub_list.filter(client=task.client)
            if task.deal:
                dub_list = dub_list.filter(deal=task.deal)

            for _task in dub_list:
                cnt += 1
                if _task.client:
                    print(_task.client.id, _task.client, _task)
                elif _task.deal:
                    print(_task.deal.cache.get('title'), _task)
                else:
                    print(None, _task.id)
                _task.delete()
                # print('\n')

        print('count', cnt)

        # for deal in Deal.objects.filter(service=10):
        #     if deal.start_datetime:
        #         deal.start_datetime -= timedelta(hours=1)
        #         deal.finish_datetime -= timedelta(hours=1)
        #         deal.save()
        #         print(deal.cache.get('title'))

        print('End fix')
