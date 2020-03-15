from datetime import date, datetime, timedelta
from decimal import Decimal
import json

from django.db.models import Q
from django.views.generic import ListView
from django.views.generic.edit import FormView
from django.forms.models import modelform_factory, modelformset_factory
from django.http import JsonResponse
from django.middleware import csrf
from django.shortcuts import render_to_response
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from absolutum.mixins import CoreMixin
from company.models import User, UserGroup
from deal.models import Deal, Service, ServiceMaster
from identity.models import Person
from utils.decorators.permission import perm_required
from utils.choices import get_choices, filters_choices


class UserReward(LoginRequiredMixin, ListView, CoreMixin):
    model = Deal
    permissions = []
    masters = dict()
    services = dict()
    filters = dict()
    filters_q = Q()

    @perm_required('user.reward_user')
    def dispatch(self, request, *args, **kwargs):
        self.permissions = self.model.get_permissions(request)
        self.filters = self.set_filters(request)
        self.filters_q = self.model.get_filters_q(self.request, filters=self.filters)
        return super().dispatch(request, *args, **kwargs)

    def set_filters(self, request):
        _start = date.today().replace(day=1)
        _end = (_start + timedelta(days=33)).replace(day=1) - timedelta(days=1)
        filters = dict(
            data=dict(start_datetime=[_start.strftime('%d.%m.%Y'), _end.strftime('%d.%m.%Y'), ]),
            ordered=['branch', 'start_datetime', 'master'],
            fields=dict(
                branch=dict(
                    label='Филиал', key='branch__in',
                    widget=dict(
                        attrs={}, name='SelectMultiple', input_type='select',
                        choices=get_choices(request, 'company.Branch')
                    )
                ),
                start_datetime=dict(
                    label='Период', key='start_datetime',
                    widget=dict(attrs={}, name="DateInput", input_type="daterange")
                ),
                master=dict(
                    label='Правщик', key='master',
                    widget=dict(
                        attrs={}, name="Select", input_type="select", choices=get_choices(request, 'company.Master')
                    )
                ),
            )
        )
        filters = self.get_filters(request, filters=filters)
        filters = filters_choices(request, filters, self.model)
        return filters

    def get_queryset(self):
        list_related = getattr(Deal, 'list_related', []) + ['master']
        queryset = Deal.objects.filter(stage__name='done') \
            .filter(self.get_filters_q(self.request, filters=self.filters)) \
            .select_related(*list_related)
        return queryset

    def get_items(self):
        items = dict()
        masters = []
        services = []
        for deal in self.get_queryset():
            master_id = deal.master.id
            if master_id not in items:
                masters.append(master_id)
                items[master_id] = dict(
                    user=deal.master.cache.get('full_name'),
                    services=dict(),
                    count=0,
                    # total=0,
                    reward=0
                )
            items[master_id]['count'] += 1
            # items[master_id]['total'] += deal.cost
            for service_id in deal.cache.get('services', []):
                services.append(service_id)
                if service_id not in items[master_id]['services']:
                    items[master_id]['services'][service_id] = 0
                items[master_id]['services'][service_id] += 1

        services = list(set(services))
        for master in Person.objects.filter(pk__in=masters):
            self.masters[master.id] = dict(
                full_name=master.cache.get('full_name', ''),
                services=dict()
            )

        for service_master in ServiceMaster.objects.filter(master__in=masters, service__in=services):
            self.masters[service_master.master.id]['services'][service_master.service.id] = dict(
                cost=service_master.cost or service_master.service.cost,
                reward=service_master.reward or Decimal('0.00'),
                reward_percent=service_master.reward_percent
            )

        for master_id, item in items.items():
            for service_id, service_item in self.masters[master_id]['services'].items():
                cost = self.masters[master_id]['services'][service_id]['cost']
                count = item['services'].get(service_id, 0)
                master_reward = self.masters[master_id]['services'][service_id]['reward']
                master_reward_percent = self.masters[master_id]['services'][service_id]['reward_percent']
                if master_reward_percent:
                    items[master_id]['reward'] += round(cost * count / 100 * master_reward, 2)
                else:
                    items[master_id]['reward'] += count * master_reward

        for service in Service.objects.filter(pk__in=services):
            self.services[service.id] = service.name

        return [i for k, i in items.items()]

    def get(self, request, *args, **kwargs):
        reward_set = dict(
            headers=[
                dict(order=None, text="Специалист", value="user"),
                dict(order=None, text="Сделок", value="count"),
                # dict(order=None, text="На сумму", value="total"),
                dict(order=None, text=" Вознаграждение", value="reward"),
            ],
            items=self.get_items(),
        )
        context = dict(
            title='Отчет: вознаграждения сотрудников',
            reward_set=reward_set,
            masters=self.masters,
            services=self.services,
            filters=self.filters,
        )

        if request.GET.get('debug'):
            from django.shortcuts import render_to_response
            return render_to_response('debug.jinja2', locals())

        return JsonResponse(context)
