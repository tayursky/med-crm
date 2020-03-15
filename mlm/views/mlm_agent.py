import calendar
from datetime import date, datetime, timedelta
from decimal import Decimal

from django.core import serializers
from django.urls import reverse, reverse_lazy
from django.http import HttpResponse, JsonResponse
from django.views.generic import DetailView, ListView, TemplateView, View
from django.views.generic.edit import FormView
from django.shortcuts import render, render_to_response, get_object_or_404
from django.forms.models import modelform_factory
from django.middleware import csrf
from django.db.models import Sum
from django.utils.translation import ugettext as _
from django.contrib.auth.mixins import LoginRequiredMixin

from absolutum.settings import DATE_FORMAT
from absolutum.settings_local import MLM_MANAGER_PERCENT
from mlm.forms import AgentForm
from mlm.models import Agent
from utils.remote_forms.forms import RemoteForm


class MLMAgentView(LoginRequiredMixin, FormView):
    model = Agent
    manager = None
    agent = None
    permissions = []
    month_set = None

    def dispatch(self, request, *args, **kwargs):
        self.kwargs.update(kwargs)
        try:
            self.agent = self.model.objects.get(pk=kwargs.get('pk'))
        except (ValueError, Agent.DoesNotExist):
            pass

        self.agent = self.agent or request.user.person.mlm_agent
        self.permissions = self.model.get_permissions(request)

        if request.method == 'GET':
            for key, value in self.request.GET.items():
                self.kwargs[key] = value[0] if isinstance(value, list) else value
        self.month_set = self.get_month_set()
        return super().dispatch(request, *args, **kwargs)

    def get_month_set(self):
        get_month = self.kwargs.get('get_month')
        day = date.today()
        print(day, get_month)
        if self.kwargs.get('day'):
            day = datetime.strptime(self.kwargs.get('day'), '%Y-%m-%d').date()
        day = day.replace(day=1)
        if get_month == 'current':
            day = date.today().replace(day=1)
        elif get_month == 'prev':
            day -= timedelta(days=1)
        elif get_month == 'next':
            day += timedelta(days=33)
        day = day.replace(day=1)
        start = datetime.combine(day, datetime.min.time())
        end = start.replace(day=calendar.monthrange(start.year, start.month)[1])
        return dict(
            day=day.strftime('%Y-%m-%d'),
            year=day.strftime('%Y'),
            month=day.strftime('%m'),
            month_name=_(day.strftime('%B')),
            start=start,
            end=datetime.combine(end, datetime.max.time())
        )

    def get_child_agents(self, with_cost=False):
        agents = Agent.objects.filter(parent=self.agent)
        items = dict()
        count = 0
        cost__total = Decimal('0.00')
        _q = dict(finish_datetime__gt=self.month_set['start'], finish_datetime__lt=self.month_set['end'])
        for agent in agents:
            count += 1
            cost__sum = agent.deals.filter(**_q, stage__name='done').aggregate(Sum('cost'))['cost__sum']
            cost__total += cost__sum if cost__sum else Decimal('0.00')
            if not with_cost or cost__sum:
                items[agent.id] = dict(
                    full_name=agent.person.cache.get('full_name'),
                    phone=agent.person.get_phone(),
                    email=agent.person.get_email(),
                    code=agent.code,
                    cache=agent.cache,
                    cost__sum=cost__sum
                )
        manager_percent = 0
        for item in MLM_MANAGER_PERCENT:
            manager_percent = item[1]
            if cost__total < item[0]:
                break
        headers = [
            dict(order='asc', text='Ф.И.О.', value='full_name'),
            dict(order=None, text='Телефон', value='phone'),
            dict(order=None, text='Email', value='email'),
            dict(order=None, text='Промокод', value='code'),
            dict(order=None, text='Оборот', value='cost__sum'),
        ]
        data = dict(
            count=count,
            ordered=[i.id for i in agents],
            headers=headers,
            items=items,
            cost__total=cost__total,
            manager_percent=manager_percent,
            salary=cost__total / 100 * manager_percent
        )
        return data

    def get_form(self, form_class=None):
        form_class = form_class or AgentForm
        kwargs = self.get_form_kwargs()
        kwargs.update({
            'initial': self.kwargs
        })
        if self.agent:
            return form_class(instance=self.agent, **kwargs)
        return form_class(**kwargs)

    def get_context_data(self, **kwargs):
        agent = dict(
            id=self.agent.id,
            position=self.agent.position,
            position__label=self.agent.get_position_display(),
            code=self.agent.code,
            discount=self.agent.discount,
            level_1=self.agent.level_1,
            level_2=self.agent.level_2,
            level_3=self.agent.level_3,
            bank_account=self.agent.bank_account,
            bank_account_fio=self.agent.bank_account_fio,
            cache=self.agent.cache,
            comment=self.agent.comment,
            total_sum=self.agent.invites.filter(status='ok').aggregate(Sum('cost'))['cost__sum']
        )
        if self.agent.referrer:
            agent.update(dict(
                referrer='%s (%s)' % (self.agent.referrer.person.__str__(), self.agent.referrer.code)
            ))
        if self.agent.parent:
            agent.update(dict(parent=dict(
                id=self.agent.parent.id,
                code=self.agent.parent.code,
                full_name=self.agent.parent.person.__str__()
            )))
        context = dict(
            agent=agent,
            person=dict(
                id=self.agent.person.id,
                full_name=self.agent.person.cache.get('full_name'),
                phone='+%s' % self.agent.person.get_phone(),
                birthday=self.agent.person.birthday.strftime(DATE_FORMAT) if self.agent.person.birthday else '',
            ),
            title=self.model._meta.verbose_name,
            error=[],
            permissions=self.permissions,
            form=RemoteForm(self.get_form(), model=self.model, csrf_token=csrf.get_token(self.request)).as_dict()
        )
        return context

    def get(self, request, *args, **kwargs):
        if not request.GET:
            return render(request, 'app_vue.jinja2')

        context = self.get_context_data()

        if self.request.GET.get('debug'):
            return render_to_response('debug.jinja2', locals())
        return JsonResponse(context, safe=False)


class MLMChildAgentView(MLMAgentView):

    def get_context_data(self, **kwargs):
        context = dict(
            month_set=self.month_set,
            child_agents=self.get_child_agents()  # with_cost=True
        )
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        if not request.GET:
            return render(request, 'app_vue.jinja2')

        if self.request.GET.get('debug'):
            return render_to_response('debug.jinja2', locals())
        return JsonResponse(context, safe=False)


class MLMChildAgentTotalView(MLMAgentView):

    def get_context_data(self, **kwargs):
        turnovers = []
        headers = [
            dict(value='date', text='Период'),
            dict(value='new_agents', text='Новых агентов'),
            dict(value='total', text='Оборот'),
            dict(value='percent', text='Процент'),
            dict(value='income', text='Начислено'),
        ]
        for item in self.agent.turnovers.filter(type='month').order_by('-date'):
            turnovers.append(dict(
                date='%s %s' % (item.date.strftime('%Y.%m'), _(item.date.strftime('%B'))),
                total=str(item.total),
                percent=item.percent,
                income=str(item.income),
                new_agents=item.new_agents
            ))
        context = dict(
            headers=headers,
            items=turnovers
        )
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        if not request.GET:
            return render(request, 'app_vue.jinja2')

        if self.request.GET.get('debug'):
            return render_to_response('debug.jinja2', locals())
        return JsonResponse(context, safe=False)
