from datetime import datetime
from django.contrib.postgres.fields import JSONField
from django_currentuser.middleware import get_current_user, get_current_authenticated_user
from django.db import models

from absolutum.mixins import CoreMixin, DisplayMixin


class Log(models.Model, CoreMixin, DisplayMixin):
    """
        Журнал телефонии
    """
    event_type = models.CharField(max_length=128, verbose_name='Тип события')
    entry_id = models.CharField(max_length=128, null=True, blank=True, verbose_name='Id звонка')
    entry_datetime = models.DateTimeField(null=True, blank=True, verbose_name='Время')
    from_number = models.CharField(max_length=256, null=True, verbose_name='Кто звонил')
    to_number = models.CharField(max_length=256, null=True, verbose_name='Набранный номер')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Запись создана')
    created_by = models.ForeignKey('company.User', null=True, blank=True, verbose_name='Инициатор',
                                   on_delete=models.CASCADE, related_name='sip_logs')
    data = JSONField(default=dict)

    filters_ordered = ['event_type']
    filters_fields = dict(
        event_type=dict(
            label='Тип события', key='event_type__icontains', widget=dict(attrs={}, name='TextInput', input_type='text')
        ),
    )
    list_display = ['entry_datetime', 'event_type', 'from_number', 'to_number', 'created_by']
    list_form_fields = ['entry_datetime', 'entry_id', 'event_type', 'from_number', 'to_number']
    list_attrs = dict(
        entry_id=dict(disabled=True),
        event_type=dict(disabled=True),
        from_number=dict(disabled=True),
        to_number=dict(disabled=True),
    )

    icon = 'el-icon-tickets'

    class Meta:
        verbose_name = 'Запись в журнале телефонии'
        verbose_name_plural = 'Журнал телефонии'
        ordering = ['-entry_datetime']
        default_permissions = ()
        permissions = [
            ('view_log', 'Просматривать журнал'),
        ]

    def save(self, *args, **kwargs):
        if not self.entry_datetime:
            self.entry_datetime = datetime.now()

        if not self.created_by:
            try:
                self.created_by = get_current_authenticated_user().person
            except:
                pass
        super().save(*args, **kwargs)
