import json
from django.core import serializers
from django.urls import reverse, reverse_lazy
from django.http import HttpResponse, JsonResponse
from django.views.generic import DetailView, ListView, TemplateView, View
from django.shortcuts import render, get_object_or_404
from django.forms.models import modelform_factory
from directory.utils import get_model, get_linked_obj, get_detail_fields_mapping, get_child_list

from directory.forms import FilterForm
from directory.views.routers import DIRECTORY_ITEMS

from django.contrib.auth.mixins import LoginRequiredMixin

from utils.remote_forms.forms import RemoteForm
from utils.choices import get_choices

from deal.models import Client


class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    object = None
    list_display = None
    count = 0
    permissions = []
    paging = dict(
        range=9,
        page_items=30,
        page=1,
        pages=1
    )
    filters = {}
    q_filters = {}

    def dispatch(self, request, *args, **kwargs):
        self.permissions = self.model.get_permissions(request)
        self.list_display = ['id'] + getattr(self.model, 'list_display', [])
        self.paging['page'] = int(request.GET.get('page', 1))
        self.filters = self.model.get_filters(request)
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        list_related = ['rel_deals', 'rel_deals__deal']
        queryset = self.model.objects \
            .filter(self.model.get_filters_q(self.request)) \
            .select_related(*list_related)
        return queryset

    def get_filters(self, request):
        try:
            filters_form = eval('%sFilterForm' % self.model.__name__)
        except NameError:
            filters_form = FilterForm
        _fields = self.model.get_filter_fields()
        _filters_class = modelform_factory(self.model, form=filters_form, fields=_fields)
        _form = _filters_class(request=request, instance=None)

        _remote_form = RemoteForm(_form, model=self.model).as_dict()
        # TODO: отфильтровать по группам доступа
        if self.model.__name__.lower() == 'timetimetable':
            _remote_form['fields']['branch']['widget']['choices'] = get_choices(self.request, 'company.Branch')

        return _remote_form

    def get_item_actions(self, pk):
        return [
            dict(
                name='edit', label='Редактировать'
            ),
            dict(
                name='detail', label='Детализация',
                url=reverse_lazy('directory:model_detail', kwargs={
                    'model_name': self.model.__name__.lower(), 'pk': pk
                }),
            )
        ]

    def get_items(self):
        items = []
        _queryset = self.get_queryset()
        if (self.request.GET.get('phones') and len(self.request.GET.get('phones')) > 6) or \
                (self.request.GET.get('full_name') and len(self.request.GET.get('full_name')) > 3):
            pass
        else:
            _queryset = _queryset.filter(
                rel_deals__deal__branch__in=get_choices(self.request, 'company.Branch', get_list=True)
            )

        self.count = _queryset.count()
        self.paging['pages'] = round(self.count / self.paging['page_items'] + 0.5)
        begin = (self.paging['page'] - 1) * self.paging['page_items']
        for q_item in _queryset[begin:begin + self.paging['page_items']]:
            item = {'actions': self.get_item_actions(q_item.pk)}
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
        if 'view' not in self.permissions:
            return JsonResponse(dict(answer='No permissions'), safe=False)
        if not request.GET:
            return render(request, 'app_vue.jinja2')

        context = dict(
            title=self.model._meta.verbose_name_plural,
            url=self.request.path,
            bread_crumbs=self.object.get_bread_crumbs() if self.object else None,
            child_list=get_child_list(self.object),
            model_name=self.model.__name__.lower(),
            pk=self.object.pk if self.object else '',
            actions=self.model.base_actions,
            headers=self.model.get_headers(),
            items=self.get_items(),
            count=self.count,
            paging=self.paging,
            permissions=self.permissions,
        )
        if self.filters:
            context.update(dict(
                filters=self.filters
            ))
        else:
            context.update(dict(
                filters=self.get_filters(request)
            ))

        if request.GET.get('debug'):
            from django.shortcuts import render_to_response
            return render_to_response('debug.jinja2', locals())

        return JsonResponse(context)
