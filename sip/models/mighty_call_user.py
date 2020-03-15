from django.contrib.postgres.fields import JSONField
from django_currentuser.middleware import get_current_user, get_current_authenticated_user
from django.db import models

from absolutum.mixins import CoreMixin, DisplayMixin


class MightyCallUser(models.Model, CoreMixin, DisplayMixin):
    """
        Пользователь яндекс телефонии Mighty Call
    """
    name = models.CharField(max_length=256, null=True, blank=True, verbose_name='Имя')
    user_key = models.CharField(max_length=256, verbose_name='Ключ пользователя',
                                help_text='Сгенерированный ключ пользователя')
    extension_number = models.CharField(max_length=18, verbose_name='Добавочный номер')
    display_number = models.CharField(max_length=18, null=True, blank=True, verbose_name='Отображаемый номер')

    token = models.TextField(null=True, blank=True, verbose_name='Токен')
    token_type = models.CharField(max_length=256, null=True, blank=True, verbose_name='Тип токена')
    token_expires = models.DateTimeField(null=True, blank=True, verbose_name='Токен действует до',
                                         help_text='Время смерти текущего токена')
    refresh_token = models.CharField(max_length=256, null=True, blank=True, verbose_name='Токен перегенерации',
                                     help_text='Токен для перегенерации ранее выданного токена')

    list_display = ['extension_number', 'user_key', 'name', 'display_number', 'token_expires']
    list_form_fields = ['extension_number', 'user_key', 'display_number', 'name',
                        'token', 'refresh_token', 'token_expires']
    list_attrs = dict(
        name=dict(disabled=True),
        token=dict(disabled=True),
        token_type=dict(disabled=True),
        # token_expires=dict(disabled=True),
        refresh_token=dict(disabled=True)
    )
    icon = 'el-icon-phone-outline'

    class Meta:
        verbose_name = 'Пользователь яндекс.телефонии'
        verbose_name_plural = 'Пользователи яндекс.телефонии'
        ordering = ['extension_number']
        default_permissions = ()
        permissions = [
            ('add_mightycalluser', 'Добавлять пользователей яндекс.телефонии'),
            ('change_mightycalluser', 'Редактировать пользователей яндекс.телефонии'),
            ('delete_mightycalluser', 'Удалять пользователей яндекс.телефонии'),
            ('view_mightycalluser', 'Просматривать пользователей яндекс.телефонии'),
        ]

    def __str__(self):
        return '%s: %s' % (self.extension_number, self.name)

    # def save(self, *args, **kwargs):
    #     super().save(*args, **kwargs)
