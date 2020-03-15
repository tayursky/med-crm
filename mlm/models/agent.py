from datetime import date, datetime, timedelta
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.contrib.auth.models import Group, Permission
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models import Avg, Sum
from django.urls import reverse, reverse_lazy
from django.core.validators import RegexValidator
from safedelete.models import SafeDeleteModel
from safedelete.models import HARD_DELETE_NOCASCADE
from simple_history.models import HistoricalRecords
from django_currentuser.middleware import get_current_user, get_current_authenticated_user

from absolutum.settings import MLM_DISCOUNT, MLM_LEVEL_1_RATE, MLM_LEVEL_2_RATE, MLM_LEVEL_3_RATE
from absolutum.settings_local import MLM_MANAGER_PERCENT
from absolutum.mixins import CoreMixin, DisplayMixin
from identity.models import Account
from company.models import EventLog
from sms.models import Sms

alphanumeric = RegexValidator(r'^[0-9a-zA-Z]*$', 'Только латинские буквы и цифры')


class Agent(SafeDeleteModel, CoreMixin, DisplayMixin):
    """
        МЛМ-агенты
    """
    POSITION = (
        ('pretender', 'Претендент'),
        ('agent', 'Агент'),
        ('manager', 'Менеджер'),
        ('head', 'Руководитель'),
    )
    person = models.OneToOneField('identity.Person', related_name='mlm_agent', verbose_name='Персона',
                                  on_delete=models.CASCADE)
    referrer = models.ForeignKey('self', null=True, blank=True, related_name='invite_agents', verbose_name='Кто привел',
                                 on_delete=models.CASCADE)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='child_agents', verbose_name='Руководитель',
                               on_delete=models.CASCADE, limit_choices_to={'position': 'manager'})
    position = models.CharField(max_length=32, choices=POSITION, default='agent', verbose_name='Положение')
    token = models.CharField(max_length=32, null=True, unique=True, verbose_name='Токен')
    offer_accepted = models.BooleanField(default=False, verbose_name='Договор оферты')
    code = models.CharField(max_length=32, null=True, unique=True, validators=[alphanumeric], verbose_name='Промокод')
    discount = models.DecimalField(default=0.00, max_digits=5, decimal_places=2, verbose_name='Скидка')
    level_1 = models.DecimalField(default=0.00, blank=True, verbose_name='Процент за 1 уровень',
                                  max_digits=5, decimal_places=2)
    level_2 = models.DecimalField(default=0.00, blank=True, verbose_name='Процент за 2 уровень',
                                  max_digits=5, decimal_places=2)
    level_3 = models.DecimalField(default=0.00, blank=True, verbose_name='Процент за 3 уровень',
                                  max_digits=5, decimal_places=2)
    bank_account = models.CharField(max_length=256, blank=True, verbose_name='Банковская карта')
    bank_account_fio = models.CharField(max_length=256, blank=True, verbose_name='Имя на карте')
    comment = models.TextField(blank=True, verbose_name='Комментарий')
    social_link = models.TextField(blank=True, verbose_name='Страница вконтакте')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Время создания')
    cache = JSONField(default=dict)

    _safedelete_policy = HARD_DELETE_NOCASCADE
    history = HistoricalRecords()

    list_display = ['position', 'manager_name', 'person', 'code', 'discount', 'levels', 'comment', 'balance']
    list_form_fields = ['referrer', 'referrer', 'parent', 'person', 'position', 'code',
                        'discount', 'level_1', 'level_2', 'level_3',
                        'bank_account', 'bank_account_fio', 'social_link', 'comment']
    list_attrs = dict(
        person=dict(remote_search='directory/remote_search/person/')
    )
    display_labels_map = dict(
        manager_name='Менеджер',
        levels='Проценты за уровни',
        balance='Баланс',
    )
    base_actions = dict(
        edit=dict(
            url=reverse_lazy('company:mlm_agent', kwargs={'pk': ':agent_id'}), name='company_mlm_agent'
        )
    )

    filters_ordered = ['position', 'person__full_name', 'person__phones', 'code']
    filters_fields = dict(
        person__full_name=dict(
            label='Ф.И.О. агента', key='person__cache__full_name__icontains',
            widget=dict(attrs={}, name='TextInput', input_type='text')
        ),
        person__phones=dict(
            label='Телефон', key='person__cache__phone__icontains',
            widget=dict(attrs={}, name='TextInput', input_type='text')
        ),
        code=dict(
            label='Промокод', key='code__icontains', widget=dict(attrs={}, name='TextInput', input_type='text')
        ),
        position=dict(
            label='Положение', key='position', widget=dict(
                attrs={}, name="Select", input_type="select", choices=[dict(label=i[1], value=i[0]) for i in POSITION]
            ))
    )
    router_name = 'mlm_agent'
    icon = 'el-icon-user'

    class Meta:
        verbose_name = 'Агент'
        verbose_name_plural = 'Агенты'
        default_permissions = ()
        ordering = ['-cache__invite_balance', 'person']
        permissions = [
            ('add_agent', 'Добавлять агентов'),
            ('change_agent', 'Редактировать агентов'),
            ('delete_agent', 'Удалять агентов'),
            ('view_agent', 'Просматривать агентов'),
            ('mlm_head', 'МЛМ руководитель'),
            ('mlm_manager', 'МЛМ менеджер'),
        ]

    def __str__(self):
        return '%s: %s%%, %s, %s' % (self.code,
                                     int(self.discount),
                                     self.person.cache.get('full_name'),
                                     self.person.get_phone())

    def cache_update(self):
        invite_cost = self.invites.filter(status='ok').aggregate(Sum('cost'))['cost__sum']
        invite_paid = self.payments.all().aggregate(Sum('cost'))['cost__sum']
        invite_cost = round(invite_cost, 2) if invite_cost else Decimal('0.00')
        invite_paid = round(invite_paid, 2) if invite_paid else Decimal('0.00')
        invite_balance = round(Decimal(self.cache.get('manager_income', '0.00')) + invite_cost - invite_paid, 2)
        self.cache.update(dict(
            invite_cost=str(invite_cost),
            invite_paid=str(invite_paid),
            invite_balance=str(invite_balance),
            total=str(invite_cost + Decimal(self.cache.get('manager_income', '0.00')))
        ))
        return True

    def get_manager_name_display(self):
        if self.parent:
            return self.parent.person.cache.get('full_name')
        return ''

    def get_levels_display(self):
        return ' - '.join([str(self.level_1), str(self.level_2), str(self.level_3)])

    def get_balance_display(self):
        return self.cache.get('invite_balance', '0.00')

    @staticmethod
    def create_agent(person):
        code = None
        agent, created = Agent.objects.get_or_create(person=person)
        if created:
            agent.referrer_id = agent.person.cache.get('mlm_referrer')
            agent.discount = Decimal(MLM_DISCOUNT)
            agent.level_1 = Decimal(MLM_LEVEL_1_RATE)
            agent.level_2 = Decimal(MLM_LEVEL_2_RATE)
            agent.level_3 = Decimal(MLM_LEVEL_3_RATE)

        if not agent.code:
            while not code or Agent.objects.filter(code=code).exists():
                code = Account.objects.make_random_password(length=6, allowed_chars='1234567890')
            agent.code = code

        agent.position = 'agent' if agent.position == 'pretender' else agent.position
        agent.token = '%s%s' % (Account.objects.make_random_password(length=3, allowed_chars='1234567890'),
                                str(person.id))
        agent.save()
        return agent

    def send_invite(self, deal=None):
        phone = self.person.get_phone()
        text_template = 'Приглашаем в партнерскую программу: {url}'
        text = text_template.format(
            url='http://crm.pravkaatlanta.ru/partner/invite/%s/' % self.token,
        )
        if phone:
            data = dict(person=self.person, phone=phone, text=text, cache=dict(mlm='invite'))
            if deal:
                data['deal'] = deal
            sms = Sms.objects.create(**data)
            return sms
        return None

    @staticmethod
    def create_pretender(person):
        agent, created = Agent.objects.get_or_create(person=person)
        if created:
            agent.position = 'pretender'
            agent.discount = Decimal(MLM_DISCOUNT)
            agent.level_1 = Decimal(MLM_LEVEL_1_RATE)
            agent.level_2 = Decimal(MLM_LEVEL_2_RATE)
            agent.level_3 = Decimal(MLM_LEVEL_3_RATE)
            agent.comment = person.comment
        else:
            agent.comment = '%s %s' % (agent.comment, person.comment)
        agent.save()
        return agent

    def calculate_turnover(self, save=False):
        current_month = date.today().replace(day=1)
        manager_income = Decimal('0.00')
        data = dict()
        result = dict()
        for child_agent in self.child_agents.all():
            _filter = dict(finish_datetime__lt=current_month, step__name='done')
            for deal in child_agent.deals.filter(**_filter).values('finish_datetime', 'cost'):
                key = deal['finish_datetime'].strftime('%Y%m')
                if key not in data.keys():
                    start_period = deal['finish_datetime'].replace(day=1, hour=0, minute=0)
                    end_period = (start_period + timedelta(days=33)).replace(day=1, hour=23, minute=59)
                    new_agents = self.child_agents.filter(created_at__gt=start_period,
                                                          created_at__lt=end_period).count()
                    data[key] = dict(agent_id=self.id,
                                     date=datetime.strptime(key, '%Y%m').date(),
                                     total=Decimal('0.00'),
                                     percent=0,
                                     new_agents=new_agents)
                    print(self.id, start_period, end_period, new_agents)
                data[key]['total'] += deal['cost']
        for key, item in data.items():
            result[key] = item
            for percent in MLM_MANAGER_PERCENT:
                result[key]['percent'] = percent[1]
                if result[key]['total'] < percent[0]:
                    break
            result[key]['income'] = result[key]['total'] / 100 * result[key]['percent']
            manager_income += result[key]['income']

        result = [item for key, item in result.items()]
        if save:
            self.turnovers.all().delete()
            self.turnovers.bulk_create([AgentTurnover(**data) for data in result])
        return manager_income, result

    def save(self, *args, **kwargs):
        self.code = self.code.upper() if self.code else None
        self.cache_update()
        if get_current_user() and self.history.first() and self.parent != self.history.first().parent:
            EventLog.objects.create(
                account=get_current_user(),
                event_type='mlm_agent_change_parent',
                event='Агент {agent_id}, {from_partner} > {to_partner}'.format(
                    agent_id=self.id,
                    from_partner=self.history.first().parent,
                    to_partner=self.parent),
                cache=dict(agent_id=self.id,
                           from_partner_id=self.history.first().parent.id if self.history.first().parent else None,
                           to_partner_id=self.parent.id if self.parent else None)
            )

        group_head = Group.objects.get(name='МЛМ: руководители')
        group_manager = Group.objects.get(name='МЛМ: менеджеры')
        if self.person.account:
            if self.position == 'head':
                self.person.account.groups.add(group_head)
            elif self.position == 'manager':
                self.person.account.groups.add(group_manager)
            elif self.position in ['agent', 'pretender']:
                self.person.account.groups.remove(group_manager, group_head)
                self.person.account.is_staff = False

            if self.position in ['manager', 'head'] or len(self.person.account.get_all_permissions()) > 0:
                self.person.account.is_staff = True

            self.person.account.save()

        super().save(*args, **kwargs)


class AgentTurnover(models.Model, CoreMixin, DisplayMixin):
    """
        Оборот агента
    """
    PERIOD_TYPE = (
        ('week', 'Недельный'),
        ('month', 'Месячный'),
        ('year', 'Годовой')
    )
    agent = models.ForeignKey('mlm.Agent', on_delete=models.CASCADE, related_name='turnovers', verbose_name='Агент')
    type = models.CharField(max_length=32, choices=PERIOD_TYPE, default='month', verbose_name='Период')
    total = models.DecimalField(default='0.00', blank=True, max_digits=30, decimal_places=2, verbose_name='Оборот')
    percent = models.DecimalField(default='0.00', blank=True, max_digits=10, decimal_places=2, verbose_name='Процент')
    income = models.DecimalField(default='0.00', blank=True, max_digits=30, decimal_places=2, verbose_name='Начислено')
    new_agents = models.IntegerField(default=0, verbose_name='Подключено агентов')
    date = models.DateField(verbose_name='Дата')

    list_display = ['agent', 'date', 'total', 'percent', 'income']
    filters_ordered = ['agent', 'date']
    filters_fields = dict(
        agent=dict(
            label='Агента', key='agent',
            widget=dict(attrs={}, name='Select', input_type="select", model_name='mlm.Agent')
        ),
        date=dict(
            label='Когда создана', key='date',
            widget=dict(attrs={}, name='DateInput', input_type='daterange')
        )
    )
    router_name = 'mlm_agent_turnover'
    icon = 'el-icon-s-finance'

    class Meta:
        verbose_name = 'Оборот агента'
        verbose_name_plural = 'Обороты агентов'
        default_permissions = ()
        permissions = []


class AgentPayment(SafeDeleteModel, CoreMixin, DisplayMixin):
    """
        Выплаты МЛМ-агентам
    """
    agent = models.ForeignKey(Agent, related_name='payments', verbose_name='Агент',
                              on_delete=models.CASCADE)
    cost = models.DecimalField(default='0.00', blank=True, max_digits=30, decimal_places=2, verbose_name='Сумма')
    comment = models.TextField(blank=True, verbose_name='Комментарий')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Время выплаты')
    created_by = models.ForeignKey('company.User', null=True, blank=True, verbose_name='Кто выплатил',
                                   on_delete=models.CASCADE, related_name='mlm_payments')

    _safedelete_policy = HARD_DELETE_NOCASCADE
    history = HistoricalRecords()

    list_display = ['agent', 'cost']
    list_form_fields = ['agent', 'cost', 'comment']
    filters_ordered = ['agent', 'created_at', 'created_by', 'agent__person__full_name']
    filters_fields = dict(
        agent=dict(
            label='Агента', key='agent',
            widget=dict(attrs={}, name='Select', input_type="select", model_name='mlm.Agent')
        ),
        agent__person__full_name=dict(
            label='Ф.И.О. агента', key='agent__person__cache__full_name__icontains',
            widget=dict(attrs={}, name='TextInput', input_type='text')
        ),
        created_at=dict(
            label='Когда создана', key='created_at',
            widget=dict(attrs={}, name='DateInput', input_type='daterange')
        ),
        created_by=dict(
            label='Кто выплатил', key='created_by',
            widget=dict(attrs={}, name='Select', input_type='select', model_name='company.User')
        ),
    )
    router_name = 'mlm_agent_payment'
    icon = 'el-icon-s-finance'

    class Meta:
        verbose_name = 'Выплата агенту'
        verbose_name_plural = 'Выплаты агентам'
        default_permissions = ()
        permissions = [
            ('add_agentpayment', 'Добавлять выплаты агентов'),
            ('change_agentpayment', 'Редактировать выплаты агентов'),
            ('delete_agentpayment', 'Удалять выплаты агентов'),
            ('view_agentpayment', 'Просматривать выплаты агентов'),
        ]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.agent.save()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.agent.save()
