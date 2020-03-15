from django.core import serializers
from django.urls import reverse, reverse_lazy
from django.http import HttpResponse, JsonResponse
from django.views.generic import DetailView, ListView, TemplateView, View
from django.views.generic.edit import FormView
from django.shortcuts import render, render_to_response, get_object_or_404
from django.forms.models import modelform_factory
from django.middleware import csrf

from django.contrib.auth.mixins import LoginRequiredMixin

from absolutum.settings import DATE_FORMAT
from mlm.forms import AgentForm
from mlm.models import Agent, Invite
from utils.choices import get_choices, filters_choices
from utils.remote_forms.forms import RemoteForm


class AgentInviteListView(LoginRequiredMixin, ListView):
    model = Invite
    agent = None
    related_name = None
    list_display = None
    count = 0
    paging = dict()
    filters = {}
    permissions = []

    def dispatch(self, request, *args, **kwargs):
        self.paging = dict(
            range=9,
            page=1,
            page_items=30,
            pages=1
        )
        self.permissions = self.model.get_permissions(request)
        self.kwargs.update(kwargs)
        try:
            self.agent = self.model.objects.get(pk=kwargs['pk'])
        except ValueError:
            pass

        self.list_display = ['id'] + getattr(self.model, 'list_display', [])
        self.paging['page'] = int(request.GET.get('page', 1))
        filters = self.model.get_filters(request)
        self.filters = filters_choices(request, filters, self.model)
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        list_related = getattr(self.model, 'list_related', [])
        queryset = self.model.objects.all()
        queryset = queryset.filter(self.model.get_filters_q(self.request)).select_related(*list_related)
        return queryset.distinct()

    def get_items(self):
        items = []
        _queryset = self.get_queryset()
        begin = 1
        self.count = _queryset.count()
        if self.count:
            self.paging['pages'] = round(self.count / self.paging['page_items'] + 0.5)
            self.paging['page'] = \
                self.paging['page'] if self.paging['page'] <= self.paging['pages'] else self.paging['pages']
            begin = (self.paging['page'] - 1) * self.paging['page_items']
        for q_item in _queryset[begin:begin + self.paging['page_items']]:
            item = dict()  # {'actions': self.get_item_actions(q_item.pk)}
            for field_name in self.list_display:
                _q_item = q_item
                for field in field_name.split('__'):
                    try:
                        _q_item = getattr(q_item, 'get_%s_display' % field)()
                    except AttributeError:
                        if hasattr(_q_item, field):
                            _q_item = getattr(_q_item, field)
                item[field_name] = _q_item.__str__() if _q_item else ''
            items.append(item)

        return items

    def get(self, request, *args, **kwargs):
        context = dict(
            agent=dict(
                id=self.agent.id,
                code=self.agent.code,
                discount=self.agent.discount,
                level_1=self.agent.level_1,
                level_2=self.agent.level_2,
                level_3=self.agent.level_3,
                bank_account=self.agent.bank_account,
                cache=self.agent.cache,
            ),
            person=dict(
                id=self.agent.person.id,
                full_name=self.agent.person.cache.get('full_name'),
                phone='+%s' % self.agent.person.get_phone(),
                birthday=self.agent.person.birthday.strftime(DATE_FORMAT) if self.agent.person.birthday else '',
            ),
            title=self.model._meta.verbose_name,
            error=[],
            permissions=self.permissions,
            form=RemoteForm(self.get_form(), model=self.model, csrf_token=csrf.get_token(self.request)).as_dict(),
        )
        if self.request.GET.get('debug'):
            return render_to_response('debug.jinja2', locals())
        return JsonResponse(context, safe=False)
