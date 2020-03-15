from datetime import datetime, time
from decimal import Decimal

from django.db import models
from simple_history.models import HistoricalRecords
from safedelete.models import SafeDeleteModel
from safedelete.models import HARD_DELETE_NOCASCADE

from absolutum.mixins import CoreMixin, DisplayMixin


class ServiceGroup(models.Model, CoreMixin, DisplayMixin):
    """
        Группы услуг
    """
    name = models.CharField(max_length=124, verbose_name='Наименование')
    comment = models.TextField(null=True, blank=True, verbose_name='Комментарий')

    list_display = ['name', 'services', 'comment']
    list_form_fields = ['name', 'comment']
    list_detail_fields = list_form_fields
    display_labels_map = dict(
        services='Услуги'
    )
    icon = 'el-icon-tickets'

    class Meta:
        verbose_name = 'Группа услуг'
        verbose_name_plural = 'Группы услуг'
        ordering = ['name']
        default_permissions = ()
        permissions = [
            ('add_servicegroup', 'Добавлять группы услуги'),
            ('change_servicegroup', 'Редактировать группы услуги'),
            ('delete_servicegroup', 'Удалять группы услуги'),
            ('view_servicegroup', 'Просматривать группы услуги'),
        ]

    def __str__(self):
        return self.name

    def get_services_display(self):
        return ', '.join([i.name for i in self.services.all()])


class Service(models.Model, CoreMixin, DisplayMixin):
    """
        Услуга
    """
    group = models.ForeignKey('deal.ServiceGroup', null=True, related_name='services', verbose_name='Группа услуг',
                              on_delete=models.PROTECT)
    name = models.CharField(max_length=124, verbose_name='Наименование')
    cost = models.DecimalField(default='0.00', max_digits=30, decimal_places=2, verbose_name='Стоимость')
    cost_kid = models.DecimalField(default='0.00', max_digits=30, decimal_places=2, verbose_name='Стоимость (ребенок)')
    time = models.TimeField(null=True, blank=True, verbose_name='Длительность процедуры')
    masters = models.ManyToManyField('company.Master', blank=True, verbose_name='Специалисты',
                                     related_name='services',
                                     through='deal.ServiceMaster',
                                     through_fields=('service', 'master'))
    comment = models.TextField(null=True, blank=True, verbose_name='Комментарий')

    history = HistoricalRecords()

    optgroups = ['group']
    filters_ordered = ['group', 'name']
    filters_fields = dict(
        group=dict(
            key='group', label='Группа',
            widget=dict(attrs=dict(), name='Select', input_type='select', model_name='deal.ServiceGroup')
        ),
        name=dict(
            key='name__icontains', label='Наименование', widget=dict(
                attrs={}, name="TextInput", input_type="text"
            )
        ),
        # masters=dict(
        #     label='Специалисты', key='masters',
        #     widget=dict(attrs={}, name='Select', input_type="select", model_name='company.Master')
        # ),
    )
    list_display = [
        'group', 'name', 'cost', 'cost_kid', 'time', 'masters_string'
    ]
    list_form_fields = [
        'group', 'name', 'cost', 'cost_kid', 'time', 'masters', 'comment'
    ]
    list_detail_fields = list_form_fields
    display_labels_map = dict(
        masters_string='Специалисты'
    )
    icon = 'el-icon-tickets'

    class Meta:
        verbose_name = 'Услуга'
        verbose_name_plural = 'Услуги'
        ordering = ['group', 'name']
        default_permissions = ()
        permissions = [
            ('add_service', 'Добавлять услуги'),
            ('change_service', 'Редактировать услуги'),
            ('delete_service', 'Удалять услуги'),
            ('view_service', 'Просматривать услуги'),
        ]

    def __str__(self):
        return self.name
        # return '%s: %s' % (self.group.name, self.name)

    def get_masters_string_display(self):
        return ', '.join([i.__str__() for i in self.masters.all()])

    @staticmethod
    def get_cost(master, services):
        _data = list()
        for item in ServiceMaster.objects.filter(master=master, service__in=services):
            services.remove(item.service.id)
            _data.append(dict(
                service_id=item.service.id,
                service=item.service.name,
                cost=item.cost or item.service.cost,
                cost_kid=item.cost_kid or item.service.cost_kid,
                # time=item.time or item.service.time
            ))
        for service in Service.objects.filter(pk__in=services):
            if service.id not in _data:
                _data.append(dict(
                    service_id=service.id,
                    service=service.name,
                    cost=service.cost,
                    cost_kid=service.cost_kid,
                    # time=service.time
                ))
        return _data


class ServiceMaster(models.Model, CoreMixin, DisplayMixin):
    """
        Оказываемая специалистом услуга
    """
    service = models.ForeignKey('deal.Service', related_name='related_masters', verbose_name='Услуга',
                                on_delete=models.CASCADE)
    master = models.ForeignKey('company.Master', related_name='related_services', verbose_name='Специалист',
                               on_delete=models.CASCADE)
    cost = models.DecimalField(max_digits=30, decimal_places=2, verbose_name='Стоимость',
                               null=True, blank=True)
    cost_kid = models.DecimalField(max_digits=30, decimal_places=2, verbose_name='Стоимость (ребенок)',
                                   null=True, blank=True)
    time = models.TimeField(null=True, blank=True, verbose_name='Длительность процедуры')

    reward = models.DecimalField(max_digits=30, decimal_places=2, verbose_name='Вознаграждение',
                                null=True, blank=True)
    reward_percent = models.BooleanField(default=False, verbose_name='Вознаграждение: процент')

    history = HistoricalRecords()

    filters_ordered = ['service', 'master']
    filters_fields = dict(
        service=dict(
            key='service', label='Услуга',
            widget=dict(attrs=dict(), name='Select', input_type='select', model_name='deal.Service')
        ),
        master=dict(
            key='master', label='Специалист',
            widget=dict(attrs=dict(), name='Select', input_type='select', model_name='company.Master')
        ),
    )
    list_display = ['service', 'master', 'cost', 'cost_kid', 'time', 'reward', 'reward_percent']
    list_form_fields = ['service', 'master', 'cost', 'cost_kid', 'time', 'reward', 'reward_percent']
    list_detail_fields = list_form_fields
    icon = 'el-icon-tickets'

    class Meta:
        verbose_name = 'Оказываемая специалистом услуга'
        verbose_name_plural = 'Оказываемые специалистом услуги'
        unique_together = ('service', 'master')
        ordering = []
        default_permissions = ()
        permissions = [
            ('add_servicemaster', 'Добавлять услуги специалиста'),
            ('change_servicemaster', 'Редактировать услуги специалиста'),
            ('delete_servicemaster', 'Удалять услуги специалиста'),
            ('view_servicemaster', 'Просматривать услуги специалиста'),
        ]

    def __str__(self):
        return '%s %s' % (self.service.__str__(), self.master.__str__())
