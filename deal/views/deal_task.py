import decimal
import json
from collections import OrderedDict
from datetime import date, datetime, timedelta

from django.db.models import Q
from django.views.generic import ListView
from django.views.generic.edit import View, FormView
from django.shortcuts import render, render_to_response
from django.middleware import csrf
from django.http import HttpResponse, JsonResponse
from django.forms.models import modelform_factory, modelformset_factory, inlineformset_factory

from absolutum.mixins import CoreMixin, DisplayMixin
from company.models import User, Branch
from deal.forms import DealForm, DealPersonForm, DealTaskForm, DealCommentForm
from deal.models import Deal, DealPerson, Service, DealTask
from identity.models import Person
from identity.utils import LoginRequiredMixin
from sms.models import Sms
from utils.choices import get_choices, filters_choices
from utils.remote_forms.forms import RemoteForm
from utils.normalize_data import normalise_data
from utils.date_time import get_datetime_string


class DealTaskListView(LoginRequiredMixin, ListView, CoreMixin):
    """
        Список задач
    """
    model = DealTask
    client = None
    deal = None
    branch = None
    today = None
    filters = dict()
    filters_q = Q()
    status_ordered = ['upcoming', 'actual', 'expired', 'done']
    status = OrderedDict(
        upcoming=dict(
            name='upcoming', label='Предстоящие', background_color='#cde6f8', color='#000'),
        expired=dict(
            name='expired', label='Просроченные', background_color='#ab2524', color='#fff'),
        actual=dict(
            name='actual', label='Актуальные', background_color='#f3a9aa', color='#000'),
        done=dict(
            name='done', label='Завершенные', background_color='#fff', color='#000'),
        reject=dict(
            name='reject', label='Отмененные', background_color='#cacaca', color='#000'),
    )
    timezone = 0
    permissions = []

    def dispatch(self, request, *args, **kwargs):
        self.permissions = Deal.get_permissions(request)
        self.timezone = request.user.person.timezone
        self.today = datetime.combine(date.today(), datetime.min.time())
        self.client = self.request.GET.get('client', None)
        self.deal = self.request.GET.get('deal', None)

        self.filters = self.set_filters(request)
        if not self.filters['data']['time_planned']:
            self.filters['data']['time_planned'] = [
                (self.today - timedelta(days=2)).strftime('%d.%m.%Y'),
                (self.today + timedelta(days=2)).strftime('%d.%m.%Y')
            ]
        self.filters_q = self.model.get_filters_q(self.request, filters=self.filters)
        return super().dispatch(request, *args, **kwargs)

    def set_filters(self, request):
        filters = dict(
            ordered=['branch', 'time_planned', 'type'],
            fields=dict(
                branch=dict(
                    label='Филиал', key='deal__branch',
                    widget=dict(attrs={}, name='Select', input_type='select', model_name='company.Branch')
                ),
                time_planned=dict(
                    label='Период', key='time_planned', widget=dict(attrs={}, name='DateInput', input_type='daterange')
                ),
                type=dict(
                    label='Тип задачи', key='type',
                    widget=dict(attrs={}, name='Select', input_type='select',
                                choices=[dict(value=i[0], label=i[1]) for i in DealTask.TASK_TYPE])
                )
            )
        )
        filters = self.get_filters(request, filters=filters)
        filters = filters_choices(request, filters, self.model)
        return filters

    def get_queryset(self):
        list_related = getattr(self.model, 'list_related', [])

        if self.client:
            queryset = self.model.objects.filter(Q(client=self.client) | Q(deal__persons=self.client))
        elif self.deal:
            queryset = self.model.objects.filter(Q(deal=self.deal) | Q(client__rel_deals__deal=self.deal))

        else:  # Тут начинается альтернатива self.filters_q
            branch = self.filters['data'].get('branch')
            time_planned = self.filters['data'].get('time_planned')
            type = self.filters['data'].get('type')

            start_time = datetime.strptime(time_planned[0], '%d.%m.%Y')
            finish_time = datetime.strptime(time_planned[1], '%d.%m.%Y')
            q = Q()
            if time_planned:
                q &= Q(time_planned__gte=start_time, time_planned__lte=finish_time)
            if branch:
                q &= Q(deal__branch=branch) | Q(client__rel_deals__deal__branch=branch)
                q |= Q(status='in_work', time_planned__lte=finish_time, deal__branch=branch)
                q |= Q(status='in_work', time_planned__lte=finish_time, client__rel_deals__deal__branch=branch)
            else:
                q |= Q(status='in_work', time_planned__lte=finish_time)

            if type:
                q &= Q(type=type)

            queryset = self.model.objects.filter(q).order_by('time_planned')

        # Фильтр только по ответственным филиалам
        if not self.client and not self.request.user.has_perm('Администраторы'):
            branch_list = get_choices(self.request, 'company.Branch', get_list=True)
            print('branch_list', branch_list)
            queryset = queryset.filter(
                Q(deal__branch__in=branch_list) |
                Q(client__rel_deals__deal__branch__in=branch_list)
            )

        return queryset.select_related(*list_related).distinct()

    def get_tasks_list(self):
        tasks = []
        values = ['id', 'client_id', 'client__cache', 'deal_id', 'deal__cache',
                  'time_planned', 'time_completed', 'title', 'comment', 'status']
        for task in self.get_queryset().values(*values):
            if task['status'] in ['done', 'reject']:
                status = task['status']
            elif task['time_planned'] and task['time_planned'].replace(hour=0, minute=0) == self.today:
                status = 'actual'
            elif task['time_planned'] and task['time_planned'].replace(hour=0, minute=0) < self.today:
                status = 'expired'
            else:
                status = 'upcoming'

            time_planned = task['time_planned'] + timedelta(hours=self.timezone)

            tasks.append(dict(
                id=task['id'],
                client=task['client_id'],
                client__cache=task['client__cache'],
                deal=task['deal_id'],
                deal__cache=task['deal__cache'],
                title=task['title'],
                comment=task['comment'],
                time_planned=time_planned.strftime('%d.%m.%Y %H:%M'),
                time_planned_int=time_planned.strftime('%Y%m%d%H%M'),
                time_completed=(task['time_completed'] + timedelta(hours=self.timezone)).strftime(
                    '%d.%m.%Y %H:%M') if task['time_completed'] else None,
                status=status
            ))

        return tasks

    def get(self, request, *args, **kwargs):
        if 'view' not in self.permissions:
            return JsonResponse(dict(answer='No permissions'), safe=False)
        if not request.GET:
            return render(request, 'app_vue.jinja2')
        context = dict(
            title='Задачи',
            status=self.status,
            status_ordered=self.status_ordered,
            filters=self.filters,
            today=self.today.strftime('%d.%m.%Y'),
            today_int=self.today.strftime('%Y%m%d%H%M'),
            tasks=self.get_tasks_list(),
        )
        return JsonResponse(context, safe=False)


def deal_task_check():
    # DealPerson

    pass
    now = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    start_date = now + timedelta(days=1)
    finish_date = start_date + timedelta(days=1)
    if not deal.start_datetime or deal.start_datetime <= datetime.now() or \
            (start_date <= deal.start_datetime and deal.start_datetime <= finish_date):
        print('\nescape sms_check_deal\n')
        return None

    if deal.step.step > 2 and not deal.sms.filter(deal_datetime=deal.start_datetime).exists():
        template_list = ['deal_confirmed_center', 'deal_confirmed_region',
                         'deal_remind_1day_center', 'deal_remind_1day_region']
        template_name = 'deal_confirmed_region' if deal.service.template.periodic else 'deal_confirmed_center'
        template_q = SmsTemplate.objects.get(name=template_name)
        template = template_q.template

        deal.sms.filter(status='wait', template__name__in=template_list).update(status='cancel')
        timezone = deal.branch.city.timezone
        for person in deal.persons.filter(rel_deals__primary=True):
            _start_datetime = deal.start_datetime + timedelta(hours=timezone)
            start_datetime = deal.start_datetime + timedelta(hours=timezone)
            timetable = ServiceTimetable.objects.filter(
                service=deal.service,
                start_datetime__lte=_start_datetime,
                finish_datetime__gte=_start_datetime
            ).first()
            if timetable:
                group = timetable.groups.filter(
                    start_time__lte=_start_datetime.time(),
                    finish_time__gt=_start_datetime.time()
                ).first()
                if group:
                    start_datetime = start_datetime.replace(hour=group.start_time.hour, minute=group.start_time.minute)
                    if start_datetime < timetable.start_datetime:
                        start_datetime = timetable.start_datetime

            datetime_string = '%s %s (%s) %s' % (
                int(start_datetime.strftime('%d')),
                get_month_name(start_datetime.strftime('%m')),
                _(start_datetime.strftime('%a')).upper(),
                start_datetime.strftime('%H:%M')
            )

            address = ''
            if timetable and timetable.address:
                address = timetable.address
            elif deal.service.branch.address:
                address = deal.service.branch.address

            text = template.format(
                start_datetime=datetime_string,
                address=address
            )
            Sms.objects.create(
                deal=deal,
                deal_datetime=deal.start_datetime,
                person=person,
                text=text,
                template=template_q
            )
