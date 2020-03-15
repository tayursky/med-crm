from django.contrib.auth.models import Group, GroupManager
from django.db import models

from absolutum.mixins import CoreMixin, DisplayMixin
from identity.models import Person


class UserManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(account__is_staff=True)


class User(Person):
    """
        Сотрудники / пользователи системы
    """
    list_display = ['full_name', 'phone_str', 'account__username', 'timezone', 'groups_string',
                    'sip_id', 'mighty_call_user', 'account__is_active']
    list_form_fields = ['last_name', 'first_name', 'patronymic', 'birthday', 'timezone', 'comment',
                        'sip_id', 'mighty_call_user']
    display_labels_map = dict(full_name='Ф.И.О.', phone_str='Телефоны', groups_string='Группы доступа')

    filters_ordered = ['full_name', 'account__groups', 'is_active']
    filters_data = dict(is_active=True)
    filters_fields = dict(
        full_name=dict(
            label='Ф.И.О.', key='cache__full_name__icontains',
            widget=dict(attrs={}, name='TextInput', input_type='text')
        ),
        account__groups=dict(
            label='Группа доступа', key='account__groups',
            widget=dict(attrs={}, name='Select', input_type='select', model_name='company.UserGroup')
        ),
        is_active=dict(
            label='Активность', key='account__is_active',
            widget=dict(
                attrs={}, name="Select", input_type="select",
                choices=[dict(label="Активен", value=True), dict(label="Отключен", value=False)]
            )
        )
    )

    objects = UserManager()

    class Meta:
        proxy = True
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"
        default_permissions = ()
        permissions = [
            ('add_user', 'Добавлять пользователей'),
            ('change_user', 'Редактировать пользователей'),
            ('delete_user', 'Удалять пользователей'),
            ('view_user', 'Просматривать пользователей'),
            ('reward_user', 'Просматривать вознаграждения сотрудников')
        ]

    def __str__(self):
        return '%s %s %s' % (self.last_name, self.first_name, self.patronymic)

    def get_groups_string_display(self):
        return ', '.join([i.name for i in self.account.groups.all()])

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class ManagerManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(
            account__is_active=True, account__groups__name='Организаторы'
        )


class Manager(Person):
    """
        Организаторы
    """
    objects = ManagerManager()

    class Meta:
        proxy = True
        verbose_name = "Организатор"
        verbose_name_plural = "Организаторы"
        default_permissions = ()
        permissions = []


class MasterManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(
            account__is_active=True, account__groups__name='Правщики'
        )


class Master(Person):
    """
        Специалисты
    """
    objects = MasterManager()

    class Meta:
        proxy = True
        verbose_name = "Специалист"
        verbose_name_plural = "Специалисты"
        default_permissions = ()
        permissions = []


class UserDisplay(Person):
    """
        Сотрудники
    """
    list_display = ['full_name', 'phone_str', 'groups_string']

    list_form_fields = ['last_name', 'first_name', 'patronymic', 'birthday', 'comment']
    display_labels_map = dict(full_name='Ф.И.О.', phone_str='Телефоны', groups_string='Группы доступа')

    objects = UserManager()

    class Meta:
        proxy = True
        verbose_name = "Сотрудники"
        verbose_name_plural = "Сотрудники"
        default_permissions = ()
        permissions = [
            ('add_userdisplay', 'Добавлять персонал'),
            ('change_userdisplay', 'Редактировать персонал'),
            ('delete_userdisplay', 'Удалять персонал'),
            ('view_userdisplay', 'Просматривать персонал'),
        ]

    def __str__(self):
        return '%s %s %s' % (self.last_name, self.first_name, self.patronymic)

    def get_groups_string_display(self):
        return ', '.join([i.name for i in self.account.groups.all()])

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class UserGroup(Group, CoreMixin, DisplayMixin):
    """
        Группы доступа
    """
    list_display = ['name']
    list_form_fields = ['name']

    class Meta:
        proxy = True
        verbose_name = "Группа доступа"
        verbose_name_plural = "Группы доступа"
        ordering = ['name']
        default_permissions = ()
        permissions = [
            ('add_usergroup', 'Добавлять группы доступа'),
            ('change_usergroup', 'Редактировать группы доступа'),
            ('delete_usergroup', 'Удалять группы доступа'),
            ('view_usergroup', 'Просматривать группы доступа'),
        ]
