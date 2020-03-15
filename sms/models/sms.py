from datetime import date, datetime, timedelta

from django.core.exceptions import ValidationError
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models import Q, signals
from simple_history.models import HistoricalRecords

from absolutum.mixins import CoreMixin, DisplayMixin


class Sms(models.Model, CoreMixin, DisplayMixin):
    """
        СМС
    """
    SMS_STATUS = (
        ('wait', 'Ожидает'),
        ('error', 'Ошибка'),
        ('ok', 'Отправлено'),
        ('cancel', 'Отменена'),
    )
    SMS_STATUS_NAME = dict(
        wait='Ожидает',
        error='Ошибка',
        ok='Отправлено',
        cancel='Отменено'
    )
    template = models.ForeignKey('sms.SmsTemplate', null=True, related_name='sms', verbose_name='Шаблон',
                                 on_delete=models.CASCADE)
    deal = models.ForeignKey('deal.Deal', null=True, related_name='sms', verbose_name='Сделка',
                             on_delete=models.CASCADE)
    deal_datetime = models.DateTimeField(null=True, blank=True, verbose_name='Время сделки', help_text='')
    person = models.ForeignKey('identity.Person', null=True, on_delete=models.CASCADE, verbose_name='Персона')
    phone = models.CharField(max_length=32, verbose_name='Номер телефона')
    status = models.CharField(max_length=32, choices=SMS_STATUS, default='wait', verbose_name='Статус смс')
    status_text = models.TextField(blank=True, verbose_name='Текст статуса')
    time_created = models.DateTimeField(auto_now_add=True, verbose_name='Время создания')
    time_sent = models.DateTimeField(null=True, blank=True, verbose_name='Время отправления')
    user = models.ForeignKey('company.User', null=True, blank=True, verbose_name='Кто создал',
                             on_delete=models.PROTECT, related_name='sms_created')
    text = models.TextField(blank=True, verbose_name='Текст сообщения')
    cache = JSONField(default=dict)

    list_filters = ['deal', 'status']
    list_display = ['time_created', 'time_sent', 'deal', 'person', 'phone', 'status', 'text']
    list_form_fields = ['text']
    list_detail_fields = list_form_fields

    class Meta:
        verbose_name = 'СМС'
        verbose_name_plural = 'СМС'
        ordering = ['-time_created']
        default_permissions = ()
        permissions = [
            ('add_sms', 'Добавлять СМС'),
            ('change_sms', 'Редактировать СМС'),
            ('delete_sms', 'Удалять СМС'),
            ('view_sms', 'Просматривать СМС'),
        ]

    def __str__(self):
        return self.text

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class SmsTemplate(models.Model, CoreMixin, DisplayMixin):
    """
        СМС: шаблон
    """
    name = models.CharField(max_length=32, verbose_name='Кодовое имя')
    label = models.CharField(max_length=128, verbose_name='Наименование')
    description = models.CharField(max_length=256, default='', blank=True, verbose_name='Описание')
    template = models.TextField(verbose_name='Шаблон')

    list_filters = []
    list_display = ['name', 'label', 'description']
    list_form_fields = ['name', 'label', 'description', 'template']
    list_detail_fields = list_form_fields
    icon = 'el-icon-chat-dot-square'

    class Meta:
        verbose_name = 'СМС: шаблон'
        verbose_name_plural = 'СМС: шаблоны'
        ordering = ['name']
        default_permissions = ()
        permissions = [
            ('add_smstemplate', 'Добавлять СМС: шаблон'),
            ('change_smstemplate', 'Редактировать СМС: шаблон'),
            ('delete_smstemplate', 'Удалять СМС: шаблон'),
            ('view_smstemplate', 'Просматривать СМС: шаблон'),
        ]

    def __str__(self):
        return self.label

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class ApiTest(models.Model, CoreMixin, DisplayMixin):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Время запроса')
    proxy = models.CharField(max_length=128, verbose_name='Прокси')

    class Meta:
        verbose_name = 'Тест'
        verbose_name_plural = 'Тест'
        ordering = ['-created_at']
        default_permissions = ()
        permissions = []
