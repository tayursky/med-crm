from django.db import models
from safedelete.models import SafeDeleteModel
from safedelete.models import HARD_DELETE_NOCASCADE
from simple_history.models import HistoricalRecords

from absolutum.mixins import CoreMixin, DisplayMixin


class DealTask(SafeDeleteModel, CoreMixin, DisplayMixin):
    """
        Задача по сделке / клиенту
    """
    TASK_TYPE = (
        ('ask_result', 'Узнать о результатах'),
        ('to_control', 'Пригласить на контроль')
    )
    TASK_STATUS = (
        ('in_work', 'В работе'),
        ('reject', 'Отменена'),
        ('done', 'Завершена')
    )
    type = models.CharField(max_length=32, choices=TASK_TYPE, null=True, blank=True, verbose_name='Тип задачи')
    status = models.CharField(max_length=32, choices=TASK_STATUS, default='in_work', verbose_name='Статус задачи')
    client = models.ForeignKey('deal.Client', null=True, blank=True, related_name='tasks', verbose_name='Клиент',
                               on_delete=models.CASCADE)
    deal = models.ForeignKey('deal.Deal', null=True, blank=True, related_name='tasks', verbose_name='Сделка',
                             on_delete=models.CASCADE)
    title = models.CharField(max_length=128, verbose_name='Заголовок')
    comment = models.TextField(default='', blank=True, verbose_name='Комментарий')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Время создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Время последнего редактирования')
    time_planned = models.DateTimeField(verbose_name='Запланированное время')
    time_completed = models.DateTimeField(null=True, blank=True, verbose_name='Время завершения')

    history = HistoricalRecords()
    _safedelete_policy = HARD_DELETE_NOCASCADE

    list_parents = ['client', 'deal']
    list_filters = ['deal', 'title', 'comment']
    list_display = ['deal', 'title', 'comment']
    list_form_fields = ['client', 'deal', 'type', 'time_planned', 'title', 'comment', 'status']
    list_detail_fields = list_form_fields
    list_attrs = dict(
        client=dict(hidden=True),
        deal=dict(hidden=True)
    )

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'
        ordering = ['time_planned', 'title']
        default_permissions = ()
        permissions = [
            ('add_dealtask', 'Добавлять задачи по сделке'),
            ('change_dealtask', 'Редактировать задачи по сделке'),
            ('delete_dealtask', 'Удалять задачи по сделке'),
            ('view_dealtask', 'Просматривать задачи по сделке'),
        ]

    def __str__(self):
        return '%s %s' % (self.title, self.status)
