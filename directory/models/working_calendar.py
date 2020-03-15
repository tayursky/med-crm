from bs4 import BeautifulSoup
from datetime import date
import requests

from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.translation import gettext as _

from absolutum.mixins import CoreMixin, DisplayMixin


class WorkingDaysCalendar(models.Model, CoreMixin, DisplayMixin):
    """
        Производственный календарь
    """
    DAY_TYPE = (
        ('workday', 'Рабочий день'),
        ('weekend', 'Выходной'),
        ('pre_holiday', 'Предпраздничный день'),
        ('holiday', 'Праздник'),
    )
    day = models.DateField(null=True)
    day_type = models.CharField(max_length=32, choices=DAY_TYPE, default='workday', verbose_name='Статус сделки')
    description = models.TextField(default='', null=True)

    class Meta:
        verbose_name = 'Производственный календарь'
        verbose_name_plural = 'Производственный календарь'
        ordering = ['day']
        default_permissions = ()
        permissions = [
            ('add_workingdayscalendar', 'Добавлять производственный календарь'),
            ('view_workingdayscalendar', 'Просматривать производственный календарь'),
        ]

    def __str__(self):
        return '%s: %s%s' % (self.day,
                             self.day_type,
                             ' (%s)' % self.description if self.description else '')

    # filters_ordered = ['day', 'day_type', 'description']
    # filters_fields = dict(
    # )
    list_detail_fields = ['day', 'day_type', 'description']
    list_display = ['day', 'day_type', 'description']
    list_form_fields = ['day', 'day_type', 'description']

    icon = 'el-icon-date'

    @staticmethod
    def calendar_parse(year):
        url = 'https://www.buhonline.ru/workcalendar/%s' % year
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'
        }
        r = requests.get(url, headers=headers)
        _html = BeautifulSoup(r.content, 'html.parser')
        _month = 0
        _begin_day = date(year, 1, 1)
        _end_day = date(year, 12, 31)
        _days = list()
        for el_months in _html.select('table.calendar table.calendar-month'):
            _month += 1
            for el_day in el_months.select('td.day-mark'):
                _day = None
                try:
                    _day = int(el_day.get_text())
                except ValueError:
                    continue
                el_class = el_day.span.attrs.get('class')
                _type = 'workday'
                if 'day-red' in el_class:
                    _type = 'weekend'
                elif 'day-blue' in el_class:
                    _type = 'holiday'
                elif 'day-grey' in el_class:
                    _type = 'pre_holiday'
                print(_month, _day, _type)
                _days.append(dict(
                    day=date(year, _month, _day),
                    day_type=_type,
                    description=el_day.attrs.get('title') or ''
                ))
        WorkingDaysCalendar.objects.filter(day__range=(_begin_day, _end_day)).delete()
        WorkingDaysCalendar.objects.bulk_create([WorkingDaysCalendar(**data) for data in _days])
        return True

    @staticmethod
    def get_calendar_set(**kwargs):
        if not kwargs.get('year'):
            return dict()
        queryset = WorkingDaysCalendar.objects.filter(day__year=kwargs.get('year'))
        if kwargs.get('month'):
            queryset = queryset.filter(day__month=kwargs.get('month'))
        if kwargs.get('week'):
            queryset = queryset.filter(day__month=kwargs.get('week'))

        months = dict()
        for day in queryset.values('day', 'day_type'):
            if day['day'].month not in months.keys():
                months[day['day'].month] = dict(
                    label=_(day['day'].strftime('%B')),
                    days=[],
                    weeks=[]
                )
            if day['day'].isocalendar()[1] not in months[day['day'].month]['weeks']:
                months[day['day'].month]['weeks'].append(day['day'].isocalendar()[1])
            months[day['day'].month]['days'].append(dict(
                day=day['day'].day,
                day_type=day['day_type'],
                weekday=day['day'].weekday(),
                week=day['day'].isocalendar()[1]
            ))

        months_collect = []
        for key, month in months.items():
            workdays = len(list(filter(lambda x: x['day_type'] == 'workday', month['days'])))
            weekends = len(list(filter(lambda x: x['day_type'] == 'weekend', month['days'])))
            pre_holidays = len(list(filter(lambda x: x['day_type'] == 'pre_holiday', month['days'])))
            holidays = len(list(filter(lambda x: x['day_type'] == 'holiday', month['days'])))
            month.update(
                annotate=dict(
                    hours=workdays * 8 + pre_holidays * 7,
                    workdays=workdays,
                    weekends=weekends,
                    pre_holidays=pre_holidays,
                    holidays=holidays
                ),
            )
            months_collect.append(month)

        annotate = dict()
        for month in months_collect:
            if not annotate:
                annotate = month['annotate'].copy()
            else:
                for key, value in month['annotate'].items():
                    annotate[key] += value

        calendar_set = dict(
            year=kwargs.get('year'),
            annotate=annotate,
            months=months_collect
        )
        return calendar_set
