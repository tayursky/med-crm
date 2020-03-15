from django.core.exceptions import ValidationError
from django.db import models
from safedelete.models import HARD_DELETE_NOCASCADE
from simple_history.models import HistoricalRecords

from identity.models import Person


class ClientManager(models.Manager):
    def get_queryset(self):
        # return super().get_queryset().filter(account=None, deleted=None)
        return super().get_queryset().filter(deleted=None)


class Client(Person):
    """
        Клиенты
    """
    _safedelete_policy = HARD_DELETE_NOCASCADE
    history = HistoricalRecords()

    list_display = ['full_name', 'phone_str', 'birthday', 'deals', 'pravka']
    list_form_fields = ['last_name', 'first_name', 'patronymic', 'birthday',
                        'address', 'passport_number', 'passport_issued', 'comment']
    display_labels_map = dict(
        full_name='Ф.И.О.',
        phone_str='Телефоны',
        deals='Сделки',
        pravka='Правка',
    )

    filters_ordered = ['branch', 'full_name', 'phones', 'deal']
    filters_fields = dict(
        branch=dict(
            label='Филиал', key='rel_deals__deal__branch',
            widget=dict(attrs={}, name='Select', input_type='select', model_name='company.Branch')
        ),
        full_name=dict(
            label='Клиент (Ф.И.О.)', key='cache__full_name__icontains',
            widget=dict(attrs={}, name='TextInput', input_type='text')
        ),
        phones=dict(
            label='Клиент (телефон)', key='phones__value__icontains',
            widget=dict(attrs={}, name='TextInput', input_type='text')
        ),
        deal=dict(
            label='id сделки', key='rel_deals__deal_id',
            widget=dict(attrs={}, name='TextInput', input_type='TextInput')
        ),
    )
    router_name = 'deal_client'
    objects = ClientManager()

    class Meta:
        proxy = True
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'
        default_permissions = ()
        permissions = [
            ('add_client', 'Добавлять клиентов'),
            ('change_client', 'Редактировать клиентов'),
            ('delete_client', 'Удалять клиентов'),
            ('view_client', 'Просматривать клиентов'),
        ]

    def __str__(self):
        return '%s %s %s' % (self.last_name, self.first_name, self.patronymic)

    def get_deals_display(self):
        string = ', '.join([rel.deal.cache['title'] for rel in self.rel_deals.all()])
        return string

    def get_pravka_display(self):
        return self.cache.get('pravka', 0)

    def clean(self):
        if Client.objects.filter(
                first_name=self.first_name, patronymic=self.patronymic, last_name=self.last_name, birthday=self.birthday
        ).exclude(pk=self.id).exists():
            raise ValidationError({'__all__': 'Клиент с таким Ф.И.О. и днем рождения уже есть'})

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
