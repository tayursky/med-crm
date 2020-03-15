from django.db import models
from simple_history.models import HistoricalRecords
from absolutum.mixins import CoreMixin, DisplayMixin


class Department(models.Model, CoreMixin, DisplayMixin):
    """
        Отдел
    """
    name = models.CharField(max_length=128, verbose_name='Наименование')
    history = HistoricalRecords()

    list_detail_fields = ['name']
    list_display = ['name']
    list_filters = ['name']
    list_form_fields = ['name']
    icon = 'el-icon-s-flag'

    class Meta:
        verbose_name = 'Отдел'
        verbose_name_plural = 'Отделы'
        ordering = ['name']
        default_permissions = ()
        permissions = [
            ('add_department', 'Добавлять отделы'),
            ('change_department', 'Редактировать отделы'),
            ('delete_department', 'Удалять отделы'),
            ('view_department', 'Просматривать отделы'),
        ]

    def __str__(self):
        return self.name
