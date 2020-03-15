import copy
import calendar
import decimal
import math
from datetime import date, datetime, timedelta

from django.db.models import Q, Max, Min
from django.http import JsonResponse
from django.views.generic import View, ListView
from django.utils.translation import ugettext as _
from django.shortcuts import render, redirect, render_to_response

from company.models import Branch, TimeTable, TimeGroup
from deal.models import Deal, Stage
from utils.choices import get_choices


class DealCalendar(View):
    """
        Базовый класс для месяца / недели / дня
    """
    branch = None
    stages = []
    year = None
    month = None
    day = None

    def dispatch(self, request, *args, **kwargs):
        stage_values = ['id', 'step', 'name', 'label', 'color', 'background_color']
        self.stages = [stage for stage in Stage.objects.all().values(*stage_values)]
        return super().dispatch(request, *args, **kwargs)

    def get_branch_set(self):
        branch_set = dict(timezone=0)
        # branch_list = get_choices(self.request, 'deal.Branch', get_list=True)

        if self.branch:
            branch_set = dict(
                id=self.branch.id,
                name=self.branch.name,
                city_name=self.branch.city.name,
                # interval=branch.interval_time.hour * 60 + branch.interval_time.minute,
                timezone=self.branch.city.timezone,
            )
        return self.branch, branch_set

    def get_range(self, period_start, period_end=None):
        period_end = period_end if period_end else period_start
        # interval_time = self.service.interval_time

        # if self.service.template.periodic:
        #     timetable_set = self.service.timetables.filter(
        #         Q(start_datetime__lte=period_start, finish_datetime__gte=period_start)
        #         | Q(start_datetime__lte=period_finish, finish_datetime__gte=period_finish)
        #         | Q(start_datetime__gte=period_start, finish_datetime__lte=period_finish)
        #     ).aggregate(Min('start_time'), Max('finish_time'), Max('interval_time'))
        #     # if timetable_set['interval_time__max']:
        #     #     interval_time = timetable_set['interval_time__max']
        #
        #     start_time = timetable_set['start_time__min'] or self.service.start_time
        #     end_time = timetable_set['finish_time__max'] or self.service.finish_time
        #     # print('start_time, end_time', start_time, end_time)
        #
        #     start = datetime(
        #         period_start.year, period_start.month, period_start.day, start_time.hour, start_time.minute
        #     )
        #     end = start.replace(hour=end_time.hour, minute=end_time.minute)
        # else:
        start = datetime(
            period_start.year, period_start.month, period_start.day,
            self.branch.start_time.hour, self.branch.start_time.minute
        )
        end = datetime(
            period_end.year, period_end.month, period_end.day,
            self.branch.end_time.hour, self.branch.end_time.minute
        )

        # interval = timedelta(hours=interval_time.hour, minutes=interval_time.minute)
        return dict(
            # interval=int(interval.seconds / 60),
            start=start.strftime('%H:%M'),
            end=end.strftime('%H:%M'),
        )

    def get_day_timing(self, deals, day):
        """
            timing для конкретного дня
        """
        groups_query_set = ServiceTimetableGroup.objects.none()
        groups = dict()
        timing = dict()
        interval_time = self.service.interval_time
        start = datetime(
            day.year, day.month, day.day, self.service.start_time.hour, self.service.start_time.minute
        )
        finish = start.replace(hour=self.service.finish_time.hour, minute=self.service.finish_time.minute)
        # print('\nperiod', start, '-', finish)
        if self.service.template.periodic:
            timetable = self.service.timetables.filter(
                Q(start_datetime__gte=start, start_datetime__lte=finish) |
                Q(finish_datetime__gte=start, finish_datetime__lte=finish) |
                Q(start_datetime__lte=start, finish_datetime__gte=start) |
                Q(start_datetime__lte=finish, finish_datetime__gte=finish)
            ).first()
            # print('timetable', timetable)

            start, finish = None, None
            if timetable:
                start_time = timetable.start_time or self.service.start_time
                finish_time = timetable.finish_time or self.service.finish_time

                if timetable.interval_time:
                    interval_time = timetable.interval_time
                timetable_start_day = date(
                    year=timetable.start_datetime.year,
                    month=timetable.start_datetime.month,
                    day=timetable.start_datetime.day
                )
                timetable_finish_day = date(
                    year=timetable.finish_datetime.year,
                    month=timetable.finish_datetime.month,
                    day=timetable.finish_datetime.day
                )
                start = datetime(
                    day.year, day.month, day.day, start_time.hour, start_time.minute
                )
                finish = start.replace(hour=finish_time.hour, minute=finish_time.minute)
                if day == timetable_start_day:
                    start = timetable.start_datetime
                elif day == timetable_finish_day:
                    finish = timetable.finish_datetime

                groups_query_set = timetable.groups.filter(finish_time__gte=start.time())
        interval = timedelta(hours=interval_time.hour, minutes=interval_time.minute)
        interval_minutes = int(interval.seconds / 60)

        # print('start, finish', start, finish)
        if not start and not finish:
            return timing, groups

        # Собираем timing
        while start < finish:
            cell_start = int(start.strftime('%Y%m%d%H%M'))
            cell_finish = int((start + interval).strftime('%Y%m%d%H%M'))
            timing[str(cell_start)[-4:]] = dict(
                deals=dict(),
                empty_cells=dict(),
                minutes=interval_minutes,
                key=start.strftime('%H%M'),
                label=start.strftime('%H:%M'),
                start=cell_start,
                finish=cell_finish,
                rows=1
            )
            # print('cell', cell_start, cell_finish)
            start += interval

        for group in groups_query_set.values('id', 'name', 'start_time', 'finish_time'):
            start_time = group['start_time'].strftime('%H%M')
            if start_time not in sorted(timing.keys()):
                start_time = sorted(timing.keys())[0]

            persons = 0
            _start_datetime = start.replace(hour=group['start_time'].hour, minute=group['start_time'].minute) \
                              - timedelta(hours=self.service_set['timezone'] + 24)
            _finish_datetime = start.replace(hour=group['finish_time'].hour, minute=group['finish_time'].minute) \
                               - timedelta(hours=self.service_set['timezone'] + 24)
            deal_qs = Deal.objects.filter(
                service=self.service, stage__step__gt=0,
                start_datetime__gte=_start_datetime, start_datetime__lt=_finish_datetime
            )
            for deal in deal_qs:
                persons += deal.persons.count()

            masters = []
            for master in ServiceTimetableGroup.objects.get(pk=group['id']).masters.all():
                masters.append(dict(
                    full_name=master.account.get_full_name()
                ))
            groups[start_time] = dict(
                name=group['name'],
                start_time=start_time,
                finish_time=group['finish_time'].strftime('%H%M'),
                persons=persons,
                masters=masters,
                masters_string=', '.join([i['full_name'] for i in masters])
            )
        # print('\ngroups', groups)

        return timing, groups
