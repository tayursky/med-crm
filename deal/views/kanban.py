from datetime import date, datetime, timedelta
import decimal

from django.db.models import Q
from django.http import JsonResponse
from django.views.generic import ListView
from django.shortcuts import render

from absolutum.mixins import CoreMixin, DisplayMixin
from identity.utils import LoginRequiredMixin
from company.models import Branch
from deal.models import Deal, DealPerson, Stage
from utils.date_time import delta_minutes, get_week_start
from utils.choices import get_choices, filters_choices


class ServiceList(LoginRequiredMixin, ListView):
    """
        Список услуг
    """
    model = Branch
    query = None
    permissions = []

    def dispatch(self, request, *args, **kwargs):
        self.permissions = Deal.get_permissions(request)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if 'view' not in self.permissions:
            return JsonResponse(dict(answer='No permissions'), safe=False)
        items = get_choices(request, 'deal.Service')
        context = {
            'items': items
        }
        return JsonResponse(context, safe=False)


class DealKanbanView(LoginRequiredMixin, ListView, CoreMixin):
    model = Deal
    branch = None
    stages = []
    timezone = 0
    count = 0
    filters = dict()
    filters_q = Q()
    permissions = []

    def dispatch(self, request, *args, **kwargs):
        self.permissions = Deal.get_permissions(request)
        self.filters = self.set_filters(request)
        if not self.filters['data']['branch']:
            # TODO make default branch
            self.filters['data']['branch'] = self.filters['fields']['branch']['widget']['choices'][0]['value']
        self.filters_q = self.model.get_filters_q(self.request, filters=self.filters)

        self.branch = Branch.objects.get(pk=self.filters['data']['branch'])
        self.timezone = self.branch.city.timezone
        stage_values = ['id', 'step', 'name', 'label', 'color', 'background_color']
        self.stages = [stage for stage in Stage.objects.exclude(name__in=['cancel', 'done']).values(*stage_values)]

        return super().dispatch(request, *args, **kwargs)

    def set_filters(self, request):
        filters = dict(
            ordered=['branch', 'start_datetime', 'deal_stage',
                     'person__full_name', 'persons__phones', 'persons__control'],
            fields=dict(
                branch=dict(
                    label='Филиал', key='branch',
                    widget=dict(attrs={}, name='Select', input_type='select', model_name='company.Branch')
                ),
                start_datetime=dict(
                    label='Период', key='start_datetime',
                    widget=dict(attrs={}, name='DateInput', input_type='daterange')
                ),
                person__full_name=dict(
                    label='Клиент (Ф.И.О.)', key='persons__cache__full_name__icontains',
                    widget=dict(attrs={}, name='TextInput', input_type='text')
                ),
                persons__phones=dict(
                    label='Клиент (телефон)', key='persons__phones__value__icontains',
                    widget=dict(attrs={}, name='TextInput', input_type='text')
                ),
                persons__control=dict(
                    label='Тип услуги', key='rel_persons__control',
                    widget=dict(
                        attrs={}, name='Select', input_type='select',
                        choices=[dict(label='Правка', value=False), dict(label='Контроль', value=True)]
                    )
                )
            )
        )
        filters = self.get_filters(request, filters=filters)
        filters = filters_choices(request, filters, self.model)
        return filters

    def get_queryset(self):
        list_related = getattr(self.model, 'list_related', [])
        queryset = self.model.objects.none()

        if self.filters_q:
            queryset = self.model.objects \
                .filter(self.get_filters_q(self.request, filters=self.filters)) \
                .exclude(stage__name__in=['cancel', 'done']) \
                .select_related(*list_related) \
                .order_by('-id')

        # Фильтр только по ответственным филиалам
        # if not self.request.user.has_perm('Администраторы'):
        #     queryset = queryset.filter(Q(services__masters=self.request.user.person.id))

        return queryset.distinct().select_related('stage')

    def get_stage_deals(self):
        deals = dict()
        for s in self.stages:
            deals[s['step'] - 1] = dict(
                items={},
                client_count=0,
                total=decimal.Decimal(0.00)
            )
        deals_collect = dict()
        for deal in self.get_queryset():
            stage_index = deal.stage.step - 1
            deals_collect[deal.id] = stage_index
            if deal.start_datetime:
                deal.start_datetime += timedelta(hours=self.timezone)
            if deal.finish_datetime:
                deal.finish_datetime += timedelta(hours=self.timezone)
            deals[stage_index]['total'] += deal.cost
            item = dict(
                id=deal.id,
                stage=deal.stage_id,
                comment=deal.comment,
                persons=[],
                pravka=deal.cache.get('pravka'),
                cost=deal.cost,
                arrear=int(deal.cost - deal.paid - deal.paid_non_cash) or None,  # Остаток
            )
            if deal.start_datetime and deal.finish_datetime:
                start = int(deal.start_datetime.strftime('%Y%m%d%H%M')) if deal.start_datetime else None
                finish = int(deal.finish_datetime.strftime('%Y%m%d%H%M')) if deal.finish_datetime else None
                item.update(
                    start=start,
                    start_string=deal.start_datetime.strftime('%d.%m.%Y %H:%M'),
                    finish=finish,
                    finish_string=deal.finish_datetime.strftime('%d.%m.%Y %H:%M'),
                    minutes=deal.cache.get('minutes', 0)
                )
            deals[stage_index]['items'][deal.id] = item

        for rel in DealPerson.objects.filter(deal__in=[i for i in deals_collect.keys()]).select_related('person'):
            stage_index = deals_collect[rel.deal_id]
            deals[stage_index]['client_count'] += 1
            deals[stage_index]['items'][rel.deal_id]['persons'].append(dict(
                control=rel.control,
                primary=rel.primary,
                id=rel.person.id,
                cache=rel.person.cache
            ))

        for k, i in deals.items():
            i['total'] = str(i['total'])
            i['items'] = [deal for deal_id, deal in i['items'].items()]

        # Сортируем сделки по id-шникам, вначале самые свежие
        for stage_key, stage in deals.items():
            deals[stage_key]['items'] = sorted(deals[stage_key]['items'], key=lambda x: x['id'], reverse=True)

        return deals

    def get(self, request, *args, **kwargs):
        if 'view' not in self.permissions:
            return JsonResponse(dict(answer='No permissions'), safe=False)
        if not request.GET:
            return render(request, 'app_vue.jinja2')

        context = dict(
            title='Канбан',
            url=self.request.path,
            stages=self.stages,
            deals=self.get_stage_deals(),
            filters=self.filters
        )

        if request.GET.get('debug'):
            from django.shortcuts import render_to_response
            return render_to_response('debug.jinja2', locals())

        return JsonResponse(context)

