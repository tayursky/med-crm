from datetime import date, datetime
from django.contrib.postgres.fields import JSONField
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext as _

from safedelete.models import SafeDeleteModel
from safedelete.models import HARD_DELETE_NOCASCADE
from simple_history.models import HistoricalRecords

from absolutum.mixins import CoreMixin, DisplayMixin
from utils.clean_data import get_numbers


class Person(SafeDeleteModel, CoreMixin, DisplayMixin):
    """
        Персональные данные
    """
    first_name = models.CharField(max_length=128, verbose_name='Имя')
    patronymic = models.CharField(max_length=128, blank=True, verbose_name='Отчество')
    last_name = models.CharField(max_length=128, verbose_name='Фамилия')
    birthday = models.DateField(null=True, blank=True, verbose_name='День рождения')
    timezone = models.SmallIntegerField(null=True, blank=True, verbose_name='Часовой пояс')
    comment = models.TextField(blank=True, verbose_name='Комментарий')
    account = models.OneToOneField('identity.Account', null=True, blank=True, verbose_name='Аккаунт',
                                   on_delete=models.CASCADE, related_name='person')
    token = models.CharField(max_length=32, null=True, unique=True, verbose_name='Токен')
    sip_id = models.CharField(max_length=128, null=True, blank=True, verbose_name='Манго-офис')
    mighty_call_user = models.ForeignKey('sip.MightyCallUser', null=True, blank=True, verbose_name='Яндекс телефония',
                                         on_delete=models.CASCADE, help_text='Пользователь яндекс телефонии')
    address = models.CharField(max_length=128, null=True, blank=True, verbose_name='Адрес регистрации')
    passport_number = models.CharField(max_length=32, null=True, blank=True, verbose_name='Паспорт серия и номер')
    passport_issued = models.CharField(max_length=128, null=True, blank=True, verbose_name='Выдавший орган')
    cache = JSONField(default=dict)

    _safedelete_policy = HARD_DELETE_NOCASCADE
    history = HistoricalRecords()

    filters_ordered = ['full_name']
    filters_fields = dict(
        full_name=dict(
            label='Ф.И.О.', key='cache__full_name__icontains',
            widget=dict(attrs={}, name='TextInput', input_type='text')
        )
    )
    list_display = ['full_name', 'phone_str', 'birthday', 'comment']
    list_form_fields = ['last_name', 'first_name', 'patronymic', 'birthday', 'timezone',
                        'address', 'passport_number', 'passport_issued', 'comment']
    list_formset = ['phones', 'emails', 'contacts', 'family']
    display_labels_map = dict(full_name='Ф.И.О.', phone_str='Телефоны')

    list_attrs = dict(
        first_name=dict(el_col=4),
        patronymic=dict(el_col=4),
        last_name=dict(el_col=4),
        birthday=dict(el_col=5, mask='11.11.1111'),
        comment=dict(el_col=7),
    )
    search_set = dict(fields=dict(full_name=dict(key='cache__full_name__icontains'),
                                  phone=dict(key='phones__value__icontains')))

    icon = 'el-icon-user'

    class Meta:
        verbose_name = 'Персона'
        verbose_name_plural = 'Персоны'
        unique_together = ('first_name', 'patronymic', 'last_name', 'birthday')
        ordering = ['last_name', 'first_name']
        default_permissions = ()
        permissions = (
            ('add_person', 'Добавлять персональные данные'),
            ('change_person', 'Изменять персональные данные'),
            ('delete_person', 'Удалять персональные данные'),
            ('view_person', 'Просматривать персональные данные'),
        )

    def __str__(self):
        return self.get_full_name_display()

    def cache_update(self):
        self.cache.update(dict(
            full_name=self.get_full_name_display(),
            pravka=self.get_pravka(),
            age=self.get_age(),
            phone=self.get_phone()
        ))
        return True

    def get_pravka(self):
        pravka = 0
        control = self.rel_deals.filter(deal__services__name='Правка', control=True, deal__stage__step__gt=0).count()
        # import ipdb; ipdb.set_trace()
        if control:
            pravka = 1 + control
        elif self.rel_deals.filter(control=False, deal__services__name='Правка').exclude(deal__stage__name='cancel') \
                .exists():
            pravka = 1
        return pravka

    def get_label_display(self):
        phone = self.get_phone()
        return '%s +%s' % (self.cache['full_name'], phone) if phone else self.cache['full_name']

    def get_cities(self):
        cities = []
        for rel_deal in self.rel_deals.all():
            cities.append(rel_deal.deal.service.branch.city_id)
        return cities

    def get_full_name_display(self):
        return ('%s %s %s' % (self.last_name, self.first_name, self.patronymic)).strip()

    def get_short_name_display(self):
        return self.get_short_name(self.get_full_name_display())

    @staticmethod
    def get_short_name(full_name):
        value = full_name.split(' ')
        return ('%s %s' % (value[0], ''.join([i[0] + '.' for index, i in enumerate(value) if index > 0]))).title()

    def get_age(self):
        try:
            today = date.today()
            return today.year - self.birthday.year - (
                    (today.month, today.day) < (self.birthday.month, self.birthday.day))
        except AttributeError:
            return ''

    def get_phone(self):
        try:
            return self.phones.first().value
        except AttributeError:
            return ''

    def get_birthday_display(self):
        return self.birthday.strftime('%d.%m.%Y')

    def get_phone_str_display(self):
        return ', '.join(i.value for i in self.phones.all())

    def get_email(self):
        try:
            return self.emails.first().value
        except AttributeError:
            return ''

    def get_email_str_display(self):
        return ', '.join(i.value for i in self.emails.all())

    def get_contact(self):
        try:
            return self.contacts.first()
        except AttributeError:
            return ''

    def clean(self):
        if Person.objects.filter(
                cache__full_name='%s %s %s' % (self.last_name, self.first_name, self.patronymic),
                birthday=self.birthday) \
                .exclude(pk=self.id).exists():
            raise ValidationError({'last_name': u'Персона с такими Ф.И.О. и датой рождения уже есть'})
        return super().clean()

    def save(self, *args, **kwargs):
        self.cache_update()
        super().save(*args, **kwargs)


class PersonFamilyRelations(models.Model, CoreMixin, DisplayMixin):
    """
        Семейные связи
    """
    RELATIVE_TYPE = (
        (0, 'отец'),
        (1, 'мать'),
    )
    person = models.ForeignKey(Person, related_name='family', verbose_name='Родственные связи',
                               on_delete=models.CASCADE)
    relative_type = models.PositiveSmallIntegerField(choices=RELATIVE_TYPE, default=0, verbose_name='Отношения')
    relative = models.ForeignKey(Person, related_name='relative', verbose_name='Родственник',
                                 on_delete=models.CASCADE)

    parent_rel = 'person'
    list_detail_fields = ['person', 'relative_type', 'relative']
    list_display = ['person', 'relative_type', 'relative']
    list_filters = ['person', 'relative_type', 'relative']
    list_form_fields = ['person', 'relative_type', 'relative']
    list_attrs = dict(
        person=dict(hidden=True),
        relative_type=dict(el_col=12),
        relative=dict(el_col=12, remote_search='directory/remote_search/person/'),
    )
    child_list = ['detail']

    class Meta:
        verbose_name = 'Семейные связи'
        verbose_name_plural = 'Семейные связи'
        default_permissions = ()

    def __str__(self):
        return '%s - %s - %s' % (self.person, self.relative_type, self.relative)


class PersonEmail(SafeDeleteModel, CoreMixin, DisplayMixin):
    """
        E-mail
    """
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='emails', verbose_name='Персона')
    value = models.EmailField(verbose_name='E-mail')
    comment = models.CharField(max_length=124, null=True, blank=True, verbose_name='Комментарий')

    _safedelete_policy = HARD_DELETE_NOCASCADE
    history = HistoricalRecords()

    parent_rel = 'person'
    list_detail_fields = ['person', 'value']
    list_display = ['value', 'comment']
    list_filters = ['value']
    list_form_fields = ['value', 'comment']
    list_attrs = dict(
        person=dict(hidden=True),
        value=dict(el_col=12),
        comment=dict(el_col=12),
    )
    child_list = ['detail']

    class Meta:
        verbose_name = 'E-mail'
        verbose_name_plural = 'E-mail'
        ordering = ['value']
        default_permissions = ()

    def __str__(self):
        return self.value


class PersonPhone(SafeDeleteModel, CoreMixin, DisplayMixin):
    """
        Телефон
    """
    PHONE_TYPE = (
        (1, 'сотовый'),
        (2, 'рабочий')
    )
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='phones', verbose_name='Персона')
    type = models.PositiveSmallIntegerField(choices=PHONE_TYPE, default=1, verbose_name='Тип телефона')
    # value = PhoneNumberField(verbose_name='Телефон')
    value = models.CharField(max_length=32, verbose_name='Телефон')
    comment = models.CharField(max_length=124, null=True, blank=True, verbose_name='Комментарий')

    _safedelete_policy = HARD_DELETE_NOCASCADE
    history = HistoricalRecords()

    parent_rel = 'person'
    list_detail_fields = ['person', 'type', 'value']
    list_display = ['type', 'value', 'comment']
    list_filters = ['type', 'value']
    list_form_fields = ['type', 'value', 'comment']
    list_attrs = dict(
        person=dict(hidden=True),
        type=dict(el_col=8),
        value=dict(el_col=8, mask='\+1 (111) 111-11111'),
        comment=dict(el_col=8),
    )

    class Meta:
        verbose_name = 'Телефон'
        verbose_name_plural = 'Телефоны'
        ordering = ['type', 'value']
        default_permissions = ()

    def __str__(self):
        return self.value

    def get_absolute_url(self):
        return '/phone/%d' % self.pk

    def save(self, *args, **kwargs):
        self.value = get_numbers(self.value)
        if self.value:
            if self.value[0] == '8':
                self.value = '7%s' % self.value[1:]
        super().save(*args, **kwargs)


class PersonContact(SafeDeleteModel, CoreMixin, DisplayMixin):
    """
        Дополнительные контакты
    """
    CONTACT_TYPE = (
        (0, ' '),
        (1, 'соц.сеть'),
        (2, 'мессенджер')
    )
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='contacts', verbose_name='Персона')
    type = models.PositiveSmallIntegerField(choices=CONTACT_TYPE, default=0, verbose_name='Тип контакта')
    value = models.CharField(max_length=32, verbose_name='Доп. контакт')
    comment = models.CharField(max_length=124, null=True, blank=True, verbose_name='Комментарий')

    _safedelete_policy = HARD_DELETE_NOCASCADE
    history = HistoricalRecords()

    parent_rel = 'person'
    list_detail_fields = ['person', 'type', 'value']
    list_display = ['type', 'value', 'comment']
    list_filters = ['type', 'value']
    list_form_fields = ['type', 'value', 'comment']
    list_attrs = dict(
        person=dict(hidden=True),
        type=dict(el_col=8),
        value=dict(el_col=8),
        comment=dict(el_col=8)
    )

    class Meta:
        verbose_name = 'Доп. контакт'
        verbose_name_plural = 'Доп. контакты'
        ordering = ['type', 'value']
        default_permissions = ()

    def __str__(self):
        return self.value
