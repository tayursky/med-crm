from django.db import models
from absolutum.mixins import CoreMixin, DisplayMixin


class City(models.Model, CoreMixin, DisplayMixin):
    """
        Город
    """
    name = models.CharField(max_length=124, unique=True, verbose_name='Наименование')
    short = models.CharField(max_length=8, null=True, blank=True, verbose_name='Сокращение')
    timezone = models.SmallIntegerField(default=0, blank=True, verbose_name='Часовой пояс')
    position = models.SmallIntegerField(default=0, blank=True, verbose_name='Сортировка')

    filters_ordered = ['name', 'timezone']
    filters_fields = dict(
        name=dict(
            label='Наименование', key='name__icontains',
            widget=dict(attrs={}, name="TextInput", input_type="text")
        ),
        timezone=dict(
            label='Часовой пояс', key='timezone',
            widget=dict(attrs={}, name="TextInput", input_type="number")
        )
    )
    list_detail_fields = ['name', 'short', 'timezone']
    list_display = ['name', 'short', 'timezone']
    list_form_fields = ['name', 'short', 'timezone', 'position']

    icon = 'el-icon-office-building'

    class Meta:
        verbose_name = 'Город'
        verbose_name_plural = 'Города'
        ordering = ['-position', 'name']
        default_permissions = ()
        permissions = [
            ('add_city', 'Добавлять города'),
            ('change_city', 'Редактировать города'),
            ('delete_city', 'Удалять города'),
            ('view_city', 'Просматривать города'),
        ]

    def __str__(self):
        return self.name
