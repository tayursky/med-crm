from decimal import Decimal
from datetime import date, datetime, timedelta

from django.apps import apps
from django.core.exceptions import ValidationError
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models import Q, signals, Prefetch
from django_currentuser.middleware import get_current_user, get_current_authenticated_user
from django_currentuser.db.models import CurrentUserField

from safedelete.models import SafeDeleteModel
from safedelete.models import HARD_DELETE_NOCASCADE
from simple_history.models import HistoricalRecords

from django.conf import settings

from company.models import TimeTable
from absolutum.mixins import CoreMixin, DisplayMixin
from deal.models.deal_signals import deal_post_save
from mlm.models import Agent


class Deal(SafeDeleteModel, CoreMixin, DisplayMixin):
    """
        Сделка
    """
    DEAL_STATUS = (
        ('in_work', 'В работе'),
        ('closed', 'Закрыта'),
    )
    DEAL_STATUS_NAME = dict(
        in_work='В работе',
        reject='Закрыта с провалом',
        ok='Успешно завершена',
    )
    branch = models.ForeignKey('company.Branch', null=True, on_delete=models.PROTECT, verbose_name='Филиал')
    status = models.CharField(max_length=32, choices=DEAL_STATUS, default='in_work', verbose_name='Статус сделки')
    stage = models.ForeignKey('deal.Stage', null=True, on_delete=models.PROTECT, verbose_name='Этап')
    services = models.ManyToManyField('deal.Service', verbose_name='Услуги')

    # service_type = models.ForeignKey('deal.ServiceTemplateType', on_delete=models.PROTECT, verbose_name='Вид услуги')
    # step = models.ForeignKey('deal.ServiceTemplateStep', on_delete=models.PROTECT, verbose_name='Этап (старый)')

    cost = models.DecimalField(default='0.00', blank=True, max_digits=30, decimal_places=2, verbose_name='Стоимость')
    paid = models.DecimalField(default='0.00', blank=True, max_digits=30, decimal_places=2, verbose_name='Оплачено')
    paid_non_cash = models.DecimalField(default='0.00', blank=True, max_digits=30, decimal_places=2,
                                        verbose_name='Оплачено безналом')
    discount = models.BooleanField(default=False, verbose_name='Скидка')
    comment = models.TextField(blank=True, verbose_name='Комментарий')

    start_datetime = models.DateTimeField(null=True, blank=True, verbose_name='Начало сеанса')
    finish_datetime = models.DateTimeField(null=True, blank=True, verbose_name='Конец сеанса')

    manager = models.ForeignKey('company.Manager', null=True, blank=True, verbose_name='Администратор',
                                on_delete=models.PROTECT, related_name='manager_deals',
                                limit_choices_to={'account__groups__name__in': ['Организаторы']})
    master = models.ForeignKey('company.Master', null=True, blank=True, verbose_name='Специалист',
                               on_delete=models.PROTECT, related_name='master_deals',
                               limit_choices_to={'account__groups__name__in': ['Правщики']})

    persons = models.ManyToManyField('identity.Person', through='deal.DealPerson',
                                     through_fields=('deal', 'person'))

    mlm_agent = models.ForeignKey('mlm.Agent', null=True, blank=True, verbose_name='МЛМ-агент',
                                  on_delete=models.PROTECT, related_name='deals')

    created_at = models.DateTimeField(auto_now_add=True, null=True, verbose_name='Время создания')
    cache = JSONField(default=dict)

    _safedelete_policy = HARD_DELETE_NOCASCADE
    history = HistoricalRecords()

    list_filters = ['services', 'discount', 'master']
    list_display = ['services', 'cost', 'start_datetime']
    list_form_fields = [
        'branch', 'master', 'services', 'stage', 'cost', 'paid', 'paid_non_cash', 'discount',
        'start_datetime', 'finish_datetime', 'comment', 'mlm_agent'
    ]
    list_attrs = dict(
        services=dict(optgroups='group', placeholder='Оказываемые услуги'),
        cost=dict(placeholder='Стоимость'),
        paid=dict(placeholder='Нал'),
        paid_non_cash=dict(placeholder='Безнал'),
        mlm_agent=dict(remote_search='mlm/check/', placeholder='Промокод')
    )
    list_detail_fields = list_form_fields
    list_formset = ['persons']
    icon = 'el-icon-circle-check'

    class Meta:
        verbose_name = 'Сделка'
        verbose_name_plural = 'Сделки'
        ordering = ['start_datetime']
        default_permissions = ()
        permissions = [
            ('add_deal', 'Добавлять сделки'),
            ('change_deal', 'Редактировать сделки'),
            ('delete_deal', 'Удалять сделки'),
            ('view_deal', 'Просматривать сделки'),
        ]

    def __str__(self):
        return '%s %s' % (self.pk, self.stage)

    def cache_update(self):
        try:
            pravka = min([i.cache.get('pravka') for i in self.persons.all() if i.cache.get('pravka')])
        except ValueError:
            pravka = 0
        self.cache.update(dict(
            title=self.get_title(),
            minutes=int((self.finish_datetime - self.start_datetime).seconds / 60) if self.start_datetime else None,
            pravka=pravka
        ))
        try:
            self.cache.update(dict(
                services=[i.id for i in self.services.all()]
            ))
        except ValueError:
            pass
        if self.id and self.mlm_agent:
            for person in self.persons.all():
                if not person.cache.get('mlm_referrer'):
                    person.cache.update(dict(mlm_referrer=self.mlm_agent.id))
                    person.save()
        return True

    @staticmethod
    def get_master(branch, start=None):
        master = None
        try:
            master = branch.workers.filter(account__groups__name='Правщики').first().id
        except AttributeError:
            pass

        return master

    def get_title(self):
        if self.start_datetime:
            return '{id}-{city}-{date}'.format(
                id=self.id,
                city=self.branch.city.short or self.branch.city.name,
                date='%s%s' % (self.start_datetime.strftime('%d%m'), self.start_datetime.strftime('%Y')[2:]),
            )
        return '{id}-{city}'.format(
            id=self.id,
            city=self.branch.city.short or self.branch.city.name
        )

    def get_persons(self):
        answer = []
        values = ['primary', 'control', 'person__id', 'person__cache']
        for item in self.rel_persons.all().prefetch_related('persons').values(*values):
            try:
                answer.append(dict(
                    id=item['person__id'],
                    primary=item['primary'],
                    control=item['control'],
                    full_name=item['person__cache'].get('full_name'),
                    age=item['person__cache'].get('age'),
                    phone=item['person__cache'].get('phone'),
                    pravka=item['person__cache'].get('pravka', 0),
                    string='{full_name} ({age}) {phone}'.format(
                        full_name=item['person__cache'].get('full_name'),
                        age=item['person__cache'].get('age'),
                        phone=item['person__cache'].get('phone')
                    ),
                ))
            except:
                pass
        return answer

    def get_persons_string_display(self):
        return ', '.join(['%s %s %s' % (i['last_name'], i['first_name'], i['patronymic'])
                          for i in self.persons.all().values('last_name', 'first_name', 'patronymic')])

    def sms_processed(self, sms, response):
        phone = [key for key in response['sms'].keys()][0]
        if response['sms'][phone]['status'] == 'OK':
            print('response[status] == OK')
            if sms.template and sms.template.name == 'deal_confirmed':
                print('deal_confirmed')
                # Если получена СМС >  статусы: Оповещение (центр) или Предоплата (регион)
                if self.stage.step < 4:
                    print('self.stage.step < 4')
                    self.stage = Stage.objects.get(name='notify')
                # Если центр, то выставляется статус Оповещение
                elif not self.branch.periodic and self.stage.step > 3:
                    print('not self.service.template.periodic and self.step.number > 3')
                    self.step = Stage.objects.get(name='notify')
        self.save()

        return True

    def get_stage(self):
        _stage = self.stage
        cost = Decimal(0.0) if not self.cost else self.cost
        paid = int(Decimal(self.paid) + Decimal(self.paid_non_cash))
        paid = True if not cost else paid  # Если cost == 0, то "предоплата состоялась"

        if _stage.name in ['cancel', 'done']:
            return _stage

        sms_confirmed = self.sms.filter(
            status='ok', template__name__in=['deal_remind_1day_center', 'deal_remind_1day_region']
        )
        if self.stage.step > 1 and not self.start_datetime:
            return Stage.objects.get(name='in work')
        if self.stage.step >= 4:
            return _stage

        if self.start_datetime:
            _stage = Stage.objects.get(name='confirmed')
        if self.start_datetime and paid and self.branch.city_id != 1:
            _stage = Stage.objects.get(name='notify')
        if self.start_datetime and paid and sms_confirmed and self.branch.city_id != 1:
            _stage = Stage.objects.get(name='notify')
        return _stage

    def clean(self):
        self.cost = Decimal('0.00') if self.cost in [None, '0.00'] else self.cost
        self.paid = Decimal('0.00') if self.paid in [None, '0.00'] else self.paid
        self.paid_non_cash = self.paid_non_cash or Decimal(0.0)

        # if self.mlm_agent:
        #     for person in self.persons.all():
        #         mlm_agent_id = person.cache.get('mlm_agent', self.mlm_agent.id)
        #         print(person, mlm_agent_id, self.mlm_agent.id)
        #         if mlm_agent_id != self.mlm_agent.id:
        #             raise ValidationError({
        #                 'cost': '{person} уже пользовался промокодом ({code})'.format(
        #                     person=person,
        #                     code=Agent.objects.get(pk=mlm_agent_id).code
        #                 )
        #             })

        if self.stage.name == 'done' and self.cost > (self.paid + self.paid_non_cash):
            raise ValidationError({'paid': 'При успешном закрытии сделки, должна быть полная оплата'})

        if self.start_datetime and self.finish_datetime:
            timezone = self.branch.city.timezone
            self.start_datetime -= timedelta(hours=timezone)
            self.finish_datetime -= timedelta(hours=timezone)
            if Deal.objects.filter(
                    Q(branch=self.branch, master=self.master, stage__step__gt=0)
                    & ((Q(start_datetime__lte=self.start_datetime, finish_datetime__gt=self.start_datetime) |
                        Q(start_datetime__lt=self.finish_datetime, finish_datetime__gt=self.finish_datetime)) |
                       Q(start_datetime__gte=self.start_datetime, finish_datetime__lte=self.finish_datetime)
                    )
            ).exclude(pk=self.pk).exists():
                raise ValidationError({'start_datetime': u'Время уже зарезервировано'})

            # Сверяемся с табелем специалиста
            if not TimeTable.objects.filter(
                    branch=self.branch, user_id=self.master.id, plan_start_datetime__date=self.start_datetime.date()
            ).exists():
                raise ValidationError({'master': u'Нет рабочего дня в табеле'})

            # Сделка должна быть в пределах одной группы
            if self.branch.time_groups.exists():
                _start_datetime = self.start_datetime + timedelta(hours=timezone)
                _end_datetime = self.finish_datetime + timedelta(hours=timezone)
                time_group = self.branch.time_groups.filter(
                    Q(timeout=False, users=self.master) &
                    Q(start_date__lte=_start_datetime, end_date__gte=_start_datetime) &
                    Q(
                        Q(start_time__lte=_start_datetime.time(), end_time__gt=_start_datetime.time()) |
                        Q(start_time__lt=_end_datetime.time(), end_time__gte=_end_datetime.time())
                    )
                ).first()
                if time_group:
                    if time_group.start_time > _start_datetime.time() or time_group.end_time < _end_datetime.time():
                        raise ValidationError({'start_datetime': u'Сделка должна быть в пределах одной группы'})

            if (self.finish_datetime - self.start_datetime).seconds / 60 < 2:
                raise ValidationError({'start_datetime': u'Минимальный интервал 2 минуты'})

    def save(self, *args, **kwargs):
        self.stage = self.get_stage()
        print('self.stage', self.stage)
        self.finish_datetime = None if not self.start_datetime else self.finish_datetime
        kwargs.update(dict(force_insert=False))

        if self.stage.name == 'done' and 'Правка' in [i['name'] for i in self.services.all().values('name')]:
            task_model = apps.get_model('deal.DealTask')
            for rel in self.rel_persons.filter(control=False):
                person = rel.person
                for key in ['ask_result', 'to_control']:
                    check_task = task_model.objects.filter(
                        type=key, client=person, title=settings.TASK_TYPE_SET[key]['title']
                    )
                    if not check_task.exists():
                        task, _ = task_model.objects.get_or_create(
                            type=key, client=person, title=settings.TASK_TYPE_SET[key]['title'],
                            time_planned=self.start_datetime + timedelta(days=settings.TASK_TYPE_SET[key]['days'])
                        )

        for rel in self.rel_persons.all():
            rel.person.save()

        self.cache_update()
        self.status = 'in_work'
        if self.stage.name in ['cancel', 'done']:
            self.status = 'closed'
        super().save(*args, **kwargs)


class DealPerson(SafeDeleteModel):
    """
        Связи сделок с персонами
    """
    deal = models.ForeignKey(Deal, related_name='rel_persons', verbose_name='Сделка',
                             on_delete=models.CASCADE)
    person = models.ForeignKey('identity.Person', related_name='rel_deals', verbose_name='Персона',
                               on_delete=models.CASCADE)
    primary = models.BooleanField(default=True, verbose_name='Основной')
    control = models.BooleanField(default=False, verbose_name='Контроль')

    history = HistoricalRecords()
    _safedelete_policy = HARD_DELETE_NOCASCADE

    class Meta:
        verbose_name = 'Привязка к персоне'
        verbose_name_plural = 'Привязки к персонам'
        ordering = ['-primary']
        default_permissions = ()

    def clean(self):
        pass
        # print('DealPerson clean()')


class DealComment(SafeDeleteModel, CoreMixin):
    """
        Комментарий к сделке / клиенту
    """
    client = models.ForeignKey('deal.Client', null=True, blank=True, related_name='comments', verbose_name='Клиент',
                               on_delete=models.CASCADE)
    deal = models.ForeignKey('deal.Deal', null=True, blank=True, related_name='comments', verbose_name='Сделка',
                             on_delete=models.CASCADE)
    comment = models.TextField(verbose_name='Комментарий')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Время создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Время последнего редактирования')

    history = HistoricalRecords()
    _safedelete_policy = HARD_DELETE_NOCASCADE

    list_parents = ['client', 'deal']
    list_form_fields = ['comment']
    list_attrs = dict(
        client=dict(hidden=True),
        deal=dict(hidden=True)
    )

    class Meta:
        verbose_name = 'Комментарий к сделке / клиенту'
        verbose_name_plural = 'Комментарии к сделкам / клиентам'
        ordering = ['-created_at']
        default_permissions = ()
        permissions = [
            ('add_dealcomment', 'Добавлять комментарии'),
            ('change_dealcomment', 'Редактировать комментарии'),
            ('delete_dealcomment', 'Удалять комментарии'),
            ('view_dealcomment', 'Просматривать комментарии'),
        ]


class Stage(models.Model, CoreMixin, DisplayMixin):
    """
        Этапы сделок
    """
    name = models.CharField(max_length=32, null=True, blank=True, verbose_name='Метка')
    label = models.CharField(max_length=32, null=True, blank=True, verbose_name='Наименование')
    step = models.IntegerField(default=0, verbose_name='Последовательность')
    color = models.CharField(max_length=7, default='#000000', blank=True, verbose_name='Цвет текста')
    background_color = models.CharField(max_length=7, default='#ffffff', blank=True, verbose_name='Цвет фона')
    comment = models.TextField(null=True, blank=True, verbose_name='Комментарий')

    list_display = ['step', 'name', 'label']
    list_form_fields = ['step', 'name', 'label', 'color', 'background_color', 'comment']
    list_detail_fields = list_form_fields
    list_attrs = dict(
        color=dict(pick_color=True),
        background_color=dict(pick_color=True)
    )
    icon = 'el-icon-tickets'

    class Meta:
        verbose_name = 'Этап сделки'
        verbose_name_plural = 'Этапы сделок'
        ordering = ['step']
        default_permissions = ()
        permissions = [
            ('add_stage', 'Добавлять этапы сделки'),
            ('change_stage', 'Редактировать этапы сделки'),
            ('delete_stage', 'Удалять этапы сделки'),
            ('view_stage', 'Просматривать этапы сделки'),
        ]

    def __str__(self):
        return '%s %s' % (self.step, self.label)


# signals.pre_save.connect(deal_pre_save, sender=Deal)
signals.post_save.connect(deal_post_save, sender=Deal)
