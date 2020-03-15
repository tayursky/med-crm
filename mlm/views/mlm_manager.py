from decimal import Decimal
from django.http import JsonResponse
from django.shortcuts import render_to_response, render, get_object_or_404
from django.middleware import csrf
from django.views.generic import DetailView, ListView, FormView

from deal.models import Deal
from utils.decorators.permission import perm_required
from mlm.forms import ManagerCreateAgentForm
from mlm.models import AgentPayment
from mlm.views.mlm_agent import MLMAgentView
from utils.remote_forms.forms import RemoteForm


class MLMCabinetManagerView(MLMAgentView):

    @perm_required('mlm.mlm_manager')
    def dispatch(self, request, *args, **kwargs):
        self.manager = request.user.person.mlm_agent
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(dict(
            title='Личный кабинет менеджера',
            month_set=self.month_set,
            permissions=self.permissions
        ))
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        context.update(
            child_agents=self.get_child_agents()
        )
        if self.request.GET.get('debug'):
            return render_to_response('debug.jinja2', locals())
        return JsonResponse(context, safe=False)


class MLMCabinetManagerInviteView(ListView):
    permissions = []
    manager = None
    count = 0
    total = Decimal('0.00')

    @perm_required('mlm.mlm_manager')
    def dispatch(self, request, *args, **kwargs):
        self.model = Deal
        self.permissions = ['view']
        self.manager = request.user.person.mlm_agent
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = self.model.objects.filter(mlm_agent=self.manager, step__name='done', cost__gt=0)
        return queryset.distinct()

    def get_items(self):
        items = []
        _queryset = self.get_queryset()
        self.count = _queryset.count()
        for item in _queryset:
            bonus = round(item.cost / 100 * self.manager.level_1, 2)
            self.total += bonus
            items.append(dict(
                id=item.id,
                cost=item.cost,
                start_datetime=item.start_datetime.strftime('%Y.%m.%d'),
                bonus=bonus
            ))
        return items

    def get(self, request, *args, **kwargs):
        if 'view' not in self.permissions:
            return JsonResponse(dict(answer='No permissions'), safe=False)

        context = dict(
            permissions=self.permissions,
            items=self.get_items(),
            count=self.count,
            total=self.total,
            headers=[
                dict(order=None, text='#', value='id'),
                dict(order=None, text='День сделки', value='start_datetime'),
                dict(order=None, text='Стоимость', value='cost'),
                dict(order=None, text='Начислено', value='bonus'),
            ]
        )
        if request.GET.get('debug'):
            from django.shortcuts import render_to_response
            return render_to_response('debug.jinja2', locals())

        return JsonResponse(context)


class MLMCabinetManagerPaymentsView(ListView):
    permissions = []
    manager = None
    count = 0
    total = Decimal('0.00')

    @perm_required('mlm.mlm_manager')
    def dispatch(self, request, *args, **kwargs):
        self.model = AgentPayment
        self.permissions = ['view']
        self.manager = request.user.person.mlm_agent
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = self.model.objects.filter(agent=self.manager)
        return queryset.distinct()

    def get_items(self):
        items = []
        _queryset = self.get_queryset()
        self.count = _queryset.count()
        for item in _queryset:
            self.total += item.cost
            items.append(dict(
                id=item.id,
                cost=item.cost,
                created_at=item.created_at.strftime('%Y.%m.%d'),
            ))
        return items

    def get(self, request, *args, **kwargs):
        if 'view' not in self.permissions:
            return JsonResponse(dict(answer='No permissions'), safe=False)

        context = dict(
            permissions=self.permissions,
            items=self.get_items(),
            count=self.count,
            total=self.total,
            headers=[
                dict(order=None, text='#', value='id'),
                dict(order=None, text='День выплаты', value='created_at'),
                dict(order=None, text='Выплата', value='cost'),
            ]
        )
        if request.GET.get('debug'):
            from django.shortcuts import render_to_response
            return render_to_response('debug.jinja2', locals())

        return JsonResponse(context)


class MLMCabinetManagerCreateAgentView(FormView):
    form_class = ManagerCreateAgentForm
    action = None
    manager = None
    permissions = []

    @perm_required('mlm.mlm_manager')
    def dispatch(self, request, *args, **kwargs):
        self.action = kwargs.get('action')
        self.manager = request.user.person.mlm_agent
        self.permissions = ['view', 'add', 'change']
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):
        if self.request.POST:
            self.request.POST._mutable = True
            self.request.POST['manager'] = self.manager
            print('self.request.POST', self.request.POST)
            return self.form_class(self.request.POST)
        return self.form_class()

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            form.save()
            return JsonResponse(dict(
                # form=form,
                message=dict(type='success', text='Сохранено'),
            ))
        return JsonResponse(dict(
            form=dict(errors=form.errors)
        ))

    def get_context_data(self, **kwargs):
        context = dict(
            title='Регистрация партнера',
            csrf_token=csrf.get_token(self.request),
            # form=self.get_form(),
            form=RemoteForm(self.get_form(), csrf_token=csrf.get_token(self.request)).as_dict(),
            permissions=self.permissions
        )
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return JsonResponse(context)
