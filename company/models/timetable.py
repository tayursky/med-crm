from datetime import date, timedelta, datetime, time
from django.contrib.postgres.fields import JSONField
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from simple_history.models import HistoricalRecords

from absolutum.settings import DATETIME_FORMAT, TIME_FORMAT
from absolutum.mixins import CoreMixin, DisplayMixin


class TimeTable(models.Model, CoreMixin, DisplayMixin):
    """
        Табель учета рабочего времени
    """
    branch = models.ForeignKey('company.Branch', related_name='timetables', verbose_name='Филиал',
                               on_delete=models.CASCADE)
    user = models.ForeignKey('company.User', on_delete=models.CASCADE, verbose_name='Работник')
    plan_start_datetime = models.DateTimeField(verbose_name='Плановое начало смены')
    plan_end_datetime = models.DateTimeField(verbose_name='Плановое окончание смены')
    fact_start_datetime = models.DateTimeField(null=True, blank=True, verbose_name='Фактическое начало смены')
    fact_end_datetime = models.DateTimeField(null=True, blank=True, verbose_name='Фактическое окончание смены')
    comment = models.TextField(default='', blank=True, verbose_name='Комментарий')
    cache = JSONField(default=dict)
    history = HistoricalRecords()

    filters_ordered = ['branch', 'user', 'plan_start_datetime']
    filters_fields = dict(
        branch=dict(
            label='Филиал', key='branch',
            widget=dict(attrs=dict(), name='Select', input_type='select', model_name='company.Branch')
        ),
        user=dict(
            label='Работник', key='user',
            widget=dict(attrs=dict(), name='Select', input_type='select', model_name='company.User')
        ),
        plan_start_datetime=dict(
            label='Месяц', key='plan_start_datetime',
            widget=dict(attrs={}, name='DateInput', input_type='daterange')
        ),
    )
    list_detail_fields = ['branch', 'user']
    list_display = ['branch', 'user']
    list_form_fields = ['branch', 'user',
                        'plan_start_datetime', 'plan_end_datetime', 'fact_start_datetime', 'fact_end_datetime',
                        'comment']
    icon = 'el-icon-date'

    class Meta:
        verbose_name = 'Табель учета рабочего времени'
        verbose_name_plural = 'Табель учета рабочего времени'
        ordering = []
        default_permissions = ()
        permissions = [
            ('add_timetable', 'Добавлять табель'),
            ('change_timetable', 'Редактировать табель'),
            ('delete_timetable', 'Удалять табель'),
            ('view_timetable', 'Просматривать табель'),
        ]

    def __str__(self):
        _start = (self.fact_start_datetime or self.plan_start_datetime) + timedelta(hours=self.branch.city.timezone)
        _end = (self.fact_end_datetime or self.plan_end_datetime) + timedelta(hours=self.branch.city.timezone)
        return '{branch}, {user}: {day} {start}-{end}'.format(
            branch=self.branch.name,
            user=self.user,
            day=_start.strftime('%d.%m.%Y'),
            start=_start.strftime(TIME_FORMAT),
            end=_end.strftime(TIME_FORMAT),
        )

    def cache_update(self):
        _time = self.get_time()
        self.cache.update(dict(
            time_int=_time['time_int'],
            time_str=_time['time_str']
        ))
        return True

    def get_time(self):
        _start = self.fact_start_datetime or self.plan_start_datetime
        _end = self.fact_end_datetime or self.plan_end_datetime
        _time = _end - _start
        time_int = _time.seconds / 3600
        dinner = 1 if time_int >= 7.5 else 0  # Обеденный час
        time_int -= dinner
        _time -= timedelta(hours=dinner)
        return dict(
            time=_time,
            time_int=time_int,
            time_str=':'.join(str(_time).split(':')[:2])
        )

    def clean(self):
        plan_start, plan_end = self.plan_start_datetime, self.plan_end_datetime
        fact_start, fact_end = self.fact_start_datetime, self.fact_end_datetime

        if plan_start >= plan_end or (fact_start and fact_end and (fact_start >= fact_end)):
            raise ValidationError({'plan_start_datetime': u'Время окончания смены должны быть больше начала'})

        timetable_qs = TimeTable.objects.filter(
            Q(user=self.user) & ((Q(plan_start_datetime__lte=plan_start, plan_end_datetime__gt=plan_start) |
                                  Q(plan_start_datetime__lt=plan_end, plan_end_datetime__gt=plan_end)) |
                                 Q(plan_start_datetime__gte=plan_start, plan_end_datetime__lte=plan_start))
        ).exclude(pk=self.pk)
        if timetable_qs.exists():
            raise ValidationError({
                'plan_start_datetime': u'Уже есть смена: %s' % timetable_qs.first()
            })

        self.plan_start_datetime = plan_start - timedelta(hours=self.branch.city.timezone)
        self.plan_end_datetime = plan_end - timedelta(hours=self.branch.city.timezone)

        if fact_start and fact_end:
            timetable_qs = TimeTable.objects.filter(
                Q(user=self.user) & ((Q(fact_start_datetime__lte=fact_start, fact_end_datetime__gt=fact_start) |
                                      Q(fact_start_datetime__lt=fact_end, fact_end_datetime__gt=fact_end)) |
                                     Q(fact_start_datetime__gte=fact_start, fact_end_datetime__lte=fact_start))
            ).exclude(pk=self.pk)
            if timetable_qs.exists():
                raise ValidationError({
                    'fact_start_datetime': u'Уже есть смена: %s' % timetable_qs.first()
                })

            self.fact_start_datetime = fact_start - timedelta(hours=self.branch.city.timezone)
            self.fact_end_datetime = fact_end - timedelta(hours=self.branch.city.timezone)

    def save(self, *args, **kwargs):
        self.cache_update()
        super().save(*args, **kwargs)


class TimeGroup(models.Model, CoreMixin, DisplayMixin):
    """
        Группы для расписания
    """
    branch = models.ForeignKey('company.Branch', related_name='time_groups', verbose_name='Филиал',
                               on_delete=models.CASCADE)
    name = models.CharField(max_length=128, blank=True, verbose_name='Наименование')
    users = models.ManyToManyField(to='company.User', blank=True, related_name='time_groups', verbose_name='Персонал')
    timeout = models.BooleanField(default=False, verbose_name='Перерыв')
    start_date = models.DateField(verbose_name='Начало периода (день)')
    end_date = models.DateField(verbose_name='Конец периода (день)')
    start_time = models.TimeField(verbose_name='Начало интервала (время)')
    end_time = models.TimeField(verbose_name='Конец интервала (время)')

    history = HistoricalRecords()

    parent_rel = 'branch'
    list_display = ['branch', 'name', 'start_date', 'end_date', 'start_time', 'end_time']
    list_form_fields = ['branch', 'name', 'users', 'timeout', 'start_date', 'end_date', 'start_time', 'end_time']
    list_detail_fields = list_form_fields
    icon = 'el-icon-circle-check'

    class Meta:
        verbose_name = 'Группа в расписании'
        verbose_name_plural = 'Группы для расписания'
        ordering = ['branch', 'start_time', '-end_time', 'start_date', '-end_date']
        default_permissions = ()
        permissions = [
            ('add_timegroup', 'Добавлять группы для расписания'),
            ('change_timegroup', 'Редактировать группы для расписания'),
            ('delete_timegroup', 'Удалять группы для расписания'),
            ('view_timegroup', 'Просматривать группы для расписания'),
        ]

    def __str__(self):
        start_date, end_date = self.start_date.strftime('%d.%m.%Y'), self.end_date.strftime('%d.%m.%Y')
        start_time, end_time = self.start_time.strftime('%H:%M'), self.end_time.strftime('%H:%M')
        if self.name:
            return '%s: %s-%s (%s-%s)' % (self.name, start_date, end_date, start_time, end_time)
        return '%s-%s (%s-%s)' % (start_date, end_date, start_time, end_time)
