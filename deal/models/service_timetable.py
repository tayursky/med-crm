from django.db import models
from safedelete.models import SafeDeleteModel
from safedelete.models import HARD_DELETE_NOCASCADE
from simple_history.models import HistoricalRecords

from absolutum.mixins import CoreMixin, DisplayMixin


class ServiceTimetable(SafeDeleteModel, CoreMixin, DisplayMixin):
    """
        Расписание для услуг
    """
    service = models.ForeignKey('deal.Service', related_name='timetables', verbose_name='Услуга',
                                on_delete=models.CASCADE)
    start_datetime = models.DateTimeField(null=True, blank=True, verbose_name='Начало периода')
    finish_datetime = models.DateTimeField(null=True, blank=True, verbose_name='Конец периода')

    start_time = models.TimeField(null=True, blank=True, verbose_name='Начало рабочего дня')
    finish_time = models.TimeField(null=True, blank=True, verbose_name='Конец рабочего дня')
    interval_time = models.TimeField(null=True, blank=True, verbose_name='Интервал')

    managers = models.ManyToManyField('company.User', blank=True, verbose_name='Администраторы',
                                      limit_choices_to={'account__groups__name__in': ['Организаторы']},
                                      related_name='manager_service_timetables')
    masters = models.ManyToManyField('company.User', blank=True, verbose_name='Правщики',
                                     limit_choices_to={'account__groups__name__in': ['Правщики']},
                                     related_name='master_service_timetables')
    address = models.TextField(null=True, blank=True, verbose_name='Адрес')
    comment = models.TextField(null=True, blank=True, verbose_name='Комментарий')

    _safedelete_policy = HARD_DELETE_NOCASCADE
    history = HistoricalRecords()

    filters_ordered = ['branch', 'managers', 'masters']
    filters_fields = dict(
        branch=dict(
            label='Филиал', key='service__branch',
            widget=dict(attrs={}, name='Select', input_type='select', model_name='company.Branch')
        ),
        managers=dict(
            label='Организаторы', key='managers',
            widget=dict(attrs={}, name='Select', input_type='select', model_name='company.Manager')
        ),
        masters=dict(
            label='Правщики', key='masters',
            widget=dict(attrs={}, name='Select', input_type='select', model_name='company.Master')
        ),
    )
    list_display = ['work_datetime', 'interval_time', 'masters_str', 'address']
    list_form_fields = [
        'start_datetime', 'finish_datetime', 'start_time', 'finish_time', 'interval_time',
        'masters', 'address', 'comment'
    ]
    list_detail_fields = list_form_fields
    display_labels_map = dict(
        work_datetime='Период',
        # work_time='Рабочее время',
        managers_str='Администраторы',
        masters_str='Правщики'
    )
    list_formset = ['groups']
    icon = 'el-icon-circle-check'

    class Meta:
        verbose_name = 'Услуга: расписание'
        verbose_name_plural = 'Услуги: расписание'
        ordering = ['start_datetime']
        default_permissions = ()
        permissions = [
            ('add_servicetimetable', 'Добавлять расписание для услуг'),
            ('change_servicetimetable', 'Редактировать расписание для услуг'),
            ('delete_servicetimetable', 'Удалять расписание для услуг'),
            ('view_servicetimetable', 'Просматривать расписание для услуг'),
        ]

    def __str__(self):
        if self.start_datetime and self.finish_datetime:
            return '%s - %s' % (self.start_datetime.strftime('%d.%m.%Y (%H:%M)'),
                                self.finish_datetime.strftime('%d.%m.%Y (%H:%M)'))
        return None

    def get_work_datetime_display(self):
        return '%s - %s' % (self.start_datetime.strftime('%d.%m.%Y (%H:%M)'),
                            self.finish_datetime.strftime('%d.%m.%Y (%H:%M)'))

    def get_work_time_display(self):
        return '%s - %s' % (self.start_time.strftime('%H:%M'), self.finish_time.strftime('%H:%M'))

    def get_interval_time_display(self):
        return self.interval_time.hour * 60 + self.interval_time.minute
        # return self.interval_time.strftime('%H:%M')

    def get_masters_str_display(self):
        return ', '.join([(i.__str__()).strip() for i in self.masters.all()])

    def get_managers_str_display(self):
        return ', '.join([(i.__str__()).strip() for i in self.managers.all()])


class ServiceTimetableGroup(SafeDeleteModel, CoreMixin, DisplayMixin):
    """
        Группы для расписания
    """
    timetable = models.ForeignKey(ServiceTimetable, related_name='groups', verbose_name='Расписание',
                                  on_delete=models.CASCADE)
    name = models.CharField(max_length=124, blank=True, verbose_name='Наименование')
    start_time = models.TimeField(null=True, blank=True, verbose_name='Начало интервала')
    finish_time = models.TimeField(null=True, blank=True, verbose_name='Конец интервала')

    masters = models.ManyToManyField('company.User', blank=True, verbose_name='Правщики',
                                     limit_choices_to={'account__groups__name__in': ['Правщики']},
                                     related_name='timetable_groups')

    _safedelete_policy = HARD_DELETE_NOCASCADE
    history = HistoricalRecords()

    parent_rel = 'timetable'
    list_display = ['timetable', 'name', 'start_time', 'finish_time', 'masters']
    list_form_fields = [
        'name', 'start_time', 'finish_time', 'masters', 'masters'
    ]
    list_detail_fields = list_form_fields
    list_attrs = dict(
        timetable=dict(hidden=True),
        name=dict(el_col=10),
        start_time=dict(el_col=7),
        finish_time=dict(el_col=7)
    )
    icon = 'el-icon-circle-check'

    class Meta:
        verbose_name = 'Услуга: группа для расписания'
        verbose_name_plural = 'Услуги: группы для расписания'
        ordering = ['timetable', 'start_time']
        default_permissions = ()
        permissions = [
            ('add_servicetimetablegroup', 'Добавлять группы для расписания'),
            ('change_servicetimetablegroup', 'Редактировать группы для расписания'),
            ('delete_servicetimetablegroup', 'Удалять группы для расписания'),
            ('view_servicetimetablegroup', 'Просматривать группы для расписания'),
        ]

    def __str__(self):
        if self.name:
            return '%s: %s - %s' % (self.name, self.start_time, self.finish_time)
        return '%s - %s' % (self.start_time, self.finish_time)
