from datetime import datetime, time

from django.db import models
from django.contrib.postgres.fields import JSONField
from simple_history.models import HistoricalRecords

from absolutum.mixins import CoreMixin, DisplayMixin


class Branch(models.Model, CoreMixin, DisplayMixin):
    """
        Филиал
    """
    city = models.ForeignKey('directory.City', on_delete=models.CASCADE, verbose_name='Город')
    name = models.CharField(max_length=128, verbose_name='Наименование')
    phone = models.CharField(max_length=32, null=True, blank=True, verbose_name='Телефон')
    address = models.TextField(null=True, blank=True, verbose_name='Адрес')
    managers = models.ManyToManyField('company.User', blank=True, verbose_name='Администраторы',
                                      limit_choices_to={'account__is_active': True},
                                      related_name='manager_branches')
    workers = models.ManyToManyField('company.User', blank=True, verbose_name='Персонал',
                                     limit_choices_to={'account__is_active': True},
                                     related_name='worker_branches')
    start_time = models.TimeField(default=time(10, 00), null=True, verbose_name='Начало рабочего дня')
    end_time = models.TimeField(default=time(20, 00), null=True, verbose_name='Конец рабочего дня')
    interval = models.TimeField(default=time(00, 15), null=True, blank=True, verbose_name='Интервал')
    periodic = models.BooleanField(default=True, verbose_name='Периодический')
    position = models.SmallIntegerField(default=0, blank=True, verbose_name='Сортировка')
    is_active = models.BooleanField(default=True, verbose_name='Активный')
    cache = JSONField(default=dict)

    history = HistoricalRecords()

    filters_ordered = ['city', 'managers', 'workers']
    filters_fields = dict(
        city=dict(
            label='Город', key='city',
            widget=dict(attrs={}, name='Select', input_type='select', model_name='directory.City')
        ),
        managers=dict(
            label='Администратор', key='managers',
            widget=dict(attrs={}, name='Select', input_type='select', model_name='company.User')
        ),
        workers=dict(
            label='Персонал', key='workers',
            widget=dict(attrs={}, name='Select', input_type='select', model_name='company.Master')
        )
    )
    list_detail_fields = ['city', 'name', 'phone']
    list_display = ['city', 'name', 'managers', 'workers', 'work_time', 'phone', 'address']
    list_form_fields = ['city', 'name', 'phone', 'address', 'managers', 'workers',
                        'start_time', 'end_time', 'interval', 'periodic', 'is_active']
    list_select_related = ['city']
    display_labels_map = dict(
        managers='Администраторы',
        workers='Персонал',
        work_time='Рабочие часы'
    )
    icon = 'el-icon-school'

    class Meta:
        verbose_name = 'Филиал'
        verbose_name_plural = 'Филиалы'
        ordering = ['-position', 'city', 'name']
        default_permissions = ()
        permissions = [
            ('add_branch', 'Добавлять филиалы'),
            ('change_branch', 'Редактировать филиалы'),
            ('delete_branch', 'Удалять филиалы'),
            ('view_branch', 'Просматривать филиалы'),
        ]

    def __str__(self):
        return self.cache.get('label')

    def cache_update(self):
        self.cache.update(dict(
            label='%s (%s)' % (self.city.name, self.name)
        ))
        return True

    def get_managers_display(self):
        return ', '.join([i.__str__().strip() for i in self.managers.all()])

    def get_workers_display(self):
        return self.workers.all().count()

    def get_work_time_display(self):
        return '%s - %s' % (self.start_time.strftime('%H:%M'), self.end_time.strftime('%H:%M'))

    def save(self, *args, **kwargs):
        self.cache_update()
        super().save(*args, **kwargs)
