from django.db.models import Q
from django.http import JsonResponse
from django.views.generic import ListView
from django.shortcuts import render

from absolutum.mixins import CoreMixin, DisplayMixin
from company.models import Branch
from deal.models import Deal, Service, Stage
from identity.utils import LoginRequiredMixin
from utils.choices import filters_choices
from utils.date_time import delta_minutes


class DealListView(LoginRequiredMixin, ListView, CoreMixin):
    model = Deal
    count = 0
    client = None
    filters = dict()
    filters_q = Q()
    stages = dict()
    paging = dict()
    permissions = []

    def dispatch(self, request, *args, **kwargs):
        self.permissions = Deal.get_permissions(request)
        self.client = self.request.GET.get('client', None)
        self.paging = dict(range=9, page_items=30, page=1, pages=1)
        self.paging['page'] = int(request.GET.get('page', 1))
        self.filters = self.set_filters(request)
        self.filters_q = self.model.get_filters_q(self.request, filters=self.filters)
        return super().dispatch(request, *args, **kwargs)

    def set_filters(self, request):
        filters = dict(
            ordered=['branch', 'start_datetime', 'created_at', 'deal_step', 'stage', 'deal_id',
                     'manager', 'master', 'comment',
                     'person__full_name', 'persons__phones', 'persons__control', 'mlm_agent'],
            fields=dict(
                branch=dict(
                    label='Филиал', key='branch',
                    widget=dict(attrs={}, name='Select', input_type='select', model_name='company.Branch')
                ),
                start_datetime=dict(
                    label='Период', key='start_datetime',
                    widget=dict(attrs={}, name='DateInput', input_type='daterange')
                ),
                created_at=dict(
                    label='Когда создана', key='created_at',
                    widget=dict(attrs={}, name='DateInput', input_type='daterange')
                ),
                stage=dict(
                    label='Этап сделки', key='stage',
                    widget=dict(attrs={}, name='Select', input_type='select', model_name='deal.Stage')
                ),
                deal_id=dict(
                    label='id сделки', key='id',
                    widget=dict(attrs={}, name='TextInput', input_type='number')
                ),
                comment=dict(
                    label='Комментарий', key='comment__icontains',
                    widget=dict(attrs={}, name='TextInput', input_type='text')
                ),
                manager=dict(
                    label='Организатор', key='manager',
                    widget=dict(attrs={}, name='Select', input_type='select', model_name='company.Manager')
                ),
                master=dict(
                    label='Правщик', key='master',
                    widget=dict(attrs={}, name='Select', input_type='select', model_name='company.Master')
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
                ),
                mlm_agent=dict(
                    label='Промокод', key='mlm_agent__code__icontains',
                    widget=dict(attrs={}, name='TextInput', input_type='text')
                )
            )
        )
        filters = self.get_filters(request, filters=filters)
        filters = filters_choices(request, filters, self.model)
        return filters

    def get_queryset(self):
        queryset = self.model.objects.none()
        list_related = getattr(self.model, 'list_related', [])

        if self.client:
            queryset = self.model.objects.filter(persons=self.client).select_related(*list_related)

        elif self.filters_q:
            queryset = self.model.objects.filter(self.filters_q)  # .order_by('-id')
            # Фильтр только по ответственным филиалам
            if not self.request.user.has_perm('Администраторы'):
                queryset = queryset.filter(Q(branch__managers=self.request.user.person.id))

        return queryset.order_by('-id').select_related(*list_related).distinct()

    def get_deals(self):
        deals = []
        branch_list = []
        if not self.filters_q and not self.client:
            return deals

        _queryset = self.get_queryset()
        self.count = _queryset.count()
        self.paging['pages'] = round(self.count / self.paging['page_items'] + 0.5)
        self.paging['page'] = \
            self.paging['page'] if self.paging['page'] <= self.paging['pages'] else self.paging['pages']
        begin = ((self.paging['page'] - 1) if self.paging['page'] else 0) * self.paging['page_items']
        for deal in _queryset[begin:begin + self.paging['page_items']]:
            persons = deal.get_persons()
            branch_list.append(deal.branch_id)
            item = dict(
                title=deal.cache['title'],
                id=deal.id,
                branch=deal.branch_id,
                step=deal.stage.step,
                cost=deal.cost,
                arrear=int(deal.cost - deal.paid - deal.paid_non_cash) or 'нет',  # Остаток
                start_string=deal.start_datetime.strftime('%H:%M') if deal.start_datetime else '',
                persons=persons,
                pravka=min([i['pravka'] for i in persons or [{'pravka': 0}]]),
            )
            if deal.start_datetime and deal.finish_datetime:
                start = int(deal.start_datetime.strftime('%Y%m%d%H%M')) if deal.start_datetime else None
                finish = int(deal.finish_datetime.strftime('%Y%m%d%H%M')) if deal.finish_datetime else None
                item.update(
                    start=start,
                    start_string=deal.start_datetime.strftime('%d.%m.%Y %H:%M'),
                    finish=finish,
                    finish_string=deal.finish_datetime.strftime('%d.%m.%Y %H:%M'),
                    minutes=delta_minutes(start, finish)
                )
            deals.append(item)
        return deals

    def get(self, request, *args, **kwargs):
        if 'view' not in self.permissions:
            return JsonResponse(dict(answer='No permissions'), safe=False)
        if not request.GET:
            return render(request, 'app_vue.jinja2')

        stages = [i for i in Stage.objects.all()
            .values('id', 'step', 'name', 'label', 'color', 'background_color', 'comment')]

        context = dict(
            title='Список сделок',
            url=self.request.path,
            deals=self.get_deals(),
            stages=stages,
            filters=self.filters,
            count=self.count,
            paging=self.paging,
        )

        if request.GET.get('debug'):
            from django.shortcuts import render_to_response
            return render_to_response('debug.jinja2', locals())

        return JsonResponse(context)
