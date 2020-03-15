# -*- coding: utf-8 -*-

from datetime import date, datetime, timedelta
from django.core.management.base import BaseCommand, CommandError

from absolutum.settings import DATETIME_FORMAT
from deal.models import Deal, DealTask, ServiceTemplateStep


class Command(BaseCommand):
    help = 'fix deals'

    def handle(self, *args, **options):
        print('Begin fix for deals\n')
        deals = dict()

        steps = {i.name: 0 for i in ServiceTemplateStep.objects.all()}
        steps.update(dict(all=0))

        deal_all_qs = Deal.objects.filter(rel_persons__control=False) \
            .exclude(persons__cache__full_name__icontains='обед')  # .filter(step__number__gt=0)
        deal_all_count = deal_all_qs.count()

        deal_cancel_qs = Deal.objects.filter(step__number=0).exclude(persons__cache__full_name__icontains='обед')
        deal_cancel_count = deal_cancel_qs.count()

        print(deal_all_count)
        print(deal_cancel_count)

        cnt = 0
        for deal in deal_all_qs:
            deal_all_count -= 1
            cnt += 1
            print(deal_all_count)
            if not deal.manager:
                print('no manager', deal.id)
                continue

            if deal.manager.last_name not in deals:
                deals[deal.manager.last_name] = dict()
                deals[deal.manager.last_name].update(steps)
            if deal.step.name in ['done', 'cancel']:
                deals[deal.manager.last_name]['all'] += 1
            deals[deal.manager.last_name][deal.step.name] += 1

        average = 'Средний процент отказов: %s%%' % round(deal_cancel_count / deal_all_qs.count() * 100, 2)
        print(average)

        for manager, item in deals.items():
            report = '%s: %s | %s' % (manager, item['all'], item['cancel'])
            if item['cancel'] and item['all']:
                report = '%s = %s%%' % (report, round(item['cancel'] / item['all'] * 100, 2))
            print(report)

        # cnt = 0
        # for deal in Deal.objects.filter(step__number=0):
        #     cnt += 1
