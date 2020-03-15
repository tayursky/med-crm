from django.contrib.postgres.fields import JSONField
from django.db import models
from simple_history.models import HistoricalRecords

from absolutum.mixins import CoreMixin, DisplayMixin


class EventLog(models.Model, CoreMixin, DisplayMixin):
    """
        Журнал событий
    """
    account = models.ForeignKey('identity.Account', on_delete=models.CASCADE, verbose_name='Пользователь')
    event_type = models.CharField(max_length=128, verbose_name='Тип события')
    event = models.TextField(null=True, blank=True, verbose_name='Событие')
    event_datetime = models.DateTimeField(auto_now_add=True, null=True, verbose_name='Время события')
    cache = JSONField(default=dict)

    filters_ordered = ['account', 'event_type', 'event']
    filters_fields = dict(
        account=dict(
            label='Пользователь', key='account',
            widget=dict(attrs=dict(), name='Select', input_type='select', model_name='identity.Account')
        ),
        event_type=dict(
            label='Тип события', key='event_type__icontains', widget=dict(attrs={}, name='TextInput', input_type='text')
        ),
        event=dict(
            label='Событие', key='event__icontains', widget=dict(attrs={}, name='TextInput', input_type='text')
        ),
    )
    list_display = ['account', 'event_type', 'event', 'event_datetime']
    list_form_fields = ['account', 'event_type', 'event', 'event_datetime']
    icon = 'el-icon-document-copy'

    class Meta:
        verbose_name = 'Журнал событий'
        verbose_name_plural = 'Журнал событий'
        ordering = ['-event_datetime']
        default_permissions = ()
        permissions = [
            ('add_eventlog', 'Добавлять журнал событий'),
            ('change_eventlog', 'Редактировать журнал событий'),
            ('delete_eventlog', 'Удалять журнал событий'),
            ('view_eventlog', 'Просматривать журнал событий'),
        ]

    def __str__(self):
        return '%s %s' % (self.account, self.event_type)
