from django.db import models
from django_currentuser.middleware import get_current_user, get_current_authenticated_user
from safedelete.models import SafeDeleteModel
from safedelete.models import HARD_DELETE_NOCASCADE
from simple_history.models import HistoricalRecords

from company.models import Department

from absolutum.mixins import CoreMixin, DisplayMixin


class ExpenseType(models.Model, CoreMixin, DisplayMixin):
    """
        Типы расходов
    """
    departments = models.ManyToManyField('company.Department', blank=True, related_name='expenses_types',
                                         verbose_name='Отделы')
    name = models.CharField(max_length=124, verbose_name='Наименование')
    hidden = models.BooleanField(default=False, verbose_name='Скрытый')

    filters_ordered = ['name', 'departments']
    filters_fields = dict(
        name=dict(
            label='Наименование', key='name__icontains', widget=dict(attrs={}, name='TextInput', input_type='text')
        ),
        departments=dict(
            label='Отделы', key='departments__in',
            widget=dict(attrs={}, name='SelectMultiple', input_type='select', model_name='company.Department')
        ),
    )
    list_display = ['name', 'departments_str', 'hidden']
    list_form_fields = ['name', 'departments', 'hidden']
    list_detail_fields = list_form_fields
    display_labels_map = dict(
        departments_str='Отделы'
    )
    icon = 'el-icon-pie-chart'

    class Meta:
        verbose_name = 'Тип расходов'
        verbose_name_plural = 'Типы расходов'
        ordering = ['name']
        default_permissions = ()
        permissions = [
            ('add_expensetype', 'Добавлять типы расходов'),
            ('change_expensetype', 'Редактировать типы расходов'),
            ('delete_expensetype', 'Удалять типы расходов'),
            ('view_expensetype', 'Просматривать типы расходов')
        ]

    def __str__(self):
        return self.name

    def get_departments_str_display(self):
        return ', '.join([i['name'] for i in self.departments.all().values('name')])


class Expense(SafeDeleteModel, CoreMixin, DisplayMixin):
    """
        Расходы
    """
    department = models.ForeignKey('company.Department', default=1, on_delete=models.CASCADE, verbose_name='Отделы',
                                   related_name='expenses')
    type = models.ForeignKey('deal.ExpenseType', null=True, blank=True, verbose_name='Тип расходов',
                             on_delete=models.CASCADE)
    other_type = models.CharField(max_length=256, default='', blank=True, verbose_name='Другой тип расходов')
    branch = models.ForeignKey('company.Branch', null=True, blank=True, verbose_name='Филиал',
                               on_delete=models.CASCADE, related_name='expenses')
    day = models.DateField(verbose_name='День')
    value = models.DecimalField(default='0.00', max_digits=30, decimal_places=2, verbose_name='Сумма')
    description = models.TextField(default='', blank=True, verbose_name='Описание')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Время создания')
    created_by = models.ForeignKey('company.User', null=True, blank=True, verbose_name='Создал запись',
                                   on_delete=models.PROTECT, related_name='expenses')

    _safedelete_policy = HARD_DELETE_NOCASCADE
    history = HistoricalRecords()

    list_display = ['department', 'branch', 'type', 'other_type', 'day', 'value', 'description', 'created_by']
    list_form_fields = ['department', 'branch', 'type', 'other_type', 'day', 'value', 'description']
    list_attrs = dict(
        # type=dict(relations=dict(department='departments')),
        day=dict(input_type='daterange')
    )
    list_detail_fields = list_form_fields
    filters_ordered = ['department', 'branch', 'type', 'other_type', 'day', 'description', 'created_by']
    filters_fields = dict(
        department=dict(
            label='Отделы', key='department__in',
            widget=dict(attrs={}, name='SelectMultiple', input_type='select', model_name='company.Department')
        ),
        branch=dict(
            label='Филиал', key='branch__in',
            widget=dict(attrs={}, name='SelectMultiple', input_type='select', model_name='company.Branch')
        ),
        day=dict(
            label='Период', key='day', widget=dict(attrs={}, name='DateInput', input_type='daterange')
        ),
        type=dict(
            label='Тип', key='type',
            widget=dict(attrs=dict(),  # relations=dict(department='departments')
                        name='Select', input_type='select', model_name='deal.ExpenseType')
        ),
        other_type=dict(
            label='Другой тип', key='other_type__icontains',
            widget=dict(attrs={}, name='TextInput', input_type='text')
        ),
        description=dict(
            label='Описание', key='description__icontains',
            widget=dict(attrs={}, name='TextInput', input_type='text')
        ),
        created_by=dict(
            label='Создал запись', key='created_by',
            widget=dict(attrs={}, name='Select', input_type='select', model_name='company.User')
        )
    )
    icon = 'el-icon-pie-chart'

    class Meta:
        verbose_name = 'Расходы'
        verbose_name_plural = 'Расходы'
        ordering = ['-day']
        default_permissions = ()
        permissions = [
            ('add_expense', 'Добавлять расходы'),
            ('change_expense', 'Редактировать расходы'),
            ('delete_expense', 'Удалять расходы'),
            ('view_expense', 'Просматривать расходы'),
        ]

    def __str__(self):
        return '%s - %s - %s' % (self.branch.city, self.branch, self.value)

    def save(self, *args, **kwargs):
        if not self.created_by:
            self.created_by = get_current_authenticated_user().person
        super().save(*args, **kwargs)


class DealExpenseManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(department=1)


class DealExpense(Expense):
    """
        Расходы: Правка
    """
    _safedelete_policy = HARD_DELETE_NOCASCADE
    objects = DealExpenseManager()

    list_display = ['branch', 'type', 'other_type', 'day', 'value', 'description', 'created_by']
    list_form_fields = ['branch', 'type', 'other_type', 'day', 'value', 'description']
    list_attrs = dict(
        branch=dict(required=True),
        day=dict(input_type='daterange')
    )
    list_detail_fields = list_form_fields
    filters_ordered = ['branch', 'type', 'other_type', 'day', 'description', 'created_by']
    filters_fields = dict(
        branch=dict(
            label='Филиал', key='branch__in',
            widget=dict(attrs={}, name='SelectMultiple', input_type='select', model_name='company.Branch')
        ),
        day=dict(
            label='Период', key='day', widget=dict(attrs={}, name='DateInput', input_type='daterange')
        ),
        type=dict(
            label='Тип', key='type',
            widget=dict(attrs={}, name='Select', input_type='select', model_name='deal.ExpenseType')
        ),
        other_type=dict(
            label='Другой тип', key='other_type__icontains', widget=dict(attrs={}, name='TextInput', input_type='text')
        ),
        description=dict(
            label='Описание', key='description__icontains', widget=dict(attrs={}, name='TextInput', input_type='text')
        ),
        created_by=dict(
            label='Создал запись', key='created_by',
            widget=dict(attrs={}, name='Select', input_type='select', model_name='company.User')
        )
    )

    class Meta:
        proxy = True
        verbose_name = 'Расходы (Правка)'
        verbose_name_plural = 'Расходы (Правка)'
        default_permissions = ()
        permissions = [
            ('add_dealexpense', 'Добавлять расходы (сделки)'),
            ('change_dealexpense', 'Редактировать расходы (сделки)'),
            ('delete_dealexpense', 'Удалять расходы (сделки)'),
            ('view_dealexpense', 'Просматривать расходы (сделки)'),
        ]

    def save(self, *args, **kwargs):
        self.department = Department.objects.get(name='Правка')
        super().save(*args, **kwargs)
