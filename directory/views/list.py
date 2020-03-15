import json
from django.apps import apps
from django.core import serializers
from django.urls import reverse, reverse_lazy
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from django.views.generic import DetailView, ListView, TemplateView, View
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin

from directory.utils import get_model, get_linked_obj, get_detail_fields_mapping, get_child_list
from directory.views.routers import DIRECTORY_ITEMS
from utils.choices import get_choices, filters_choices


class ModelDetail(LoginRequiredMixin, DetailView):
    template_name = 'model_detail.jinja2'

    def dispatch(self, request, *args, **kwargs):
        self.model = get_model(kwargs.get('model_name', None))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        context.update({
            'url': self.request.path,
            'title': self.model._meta.verbose_name,
            'model_name': self.model.__name__.lower(),
            'menu_items': DIRECTORY_ITEMS,
            'detail_list': get_detail_fields_mapping(context['object']),
            'child_list': get_child_list(self.object),
            'bread_crumbs': self.object.get_bread_crumbs()
        })
        obj = get_object_or_404(self.model, pk=self.kwargs.get('pk'))
        return context


class ModelList(LoginRequiredMixin, ListView):
    parent_model = None
    object = None
    related_name = None
    list_display = None
    count = 0
    permissions = []
    paging = dict()
    filters = {}

    def dispatch(self, request, *args, **kwargs):
        self.paging = dict(
            range=9,
            page=1,
            page_items=100,
            pages=1
        )
        # try:
        #     self.model = apps.get_model(request.GET.get('meta_label'))
        # except (ValueError, LookupError):
        self.model = get_model(kwargs.get('model_name') or request.GET.get('model_name'))
        self.permissions = self.model.get_permissions(request)
        parent_model_name = request.GET.get('parent_model_name', kwargs.get('parent_model_name'))
        if parent_model_name:
            self.parent_model = get_model(parent_model_name)
            pk = request.GET.get('parent_pk', kwargs.get('parent_pk'))
            self.object = self.parent_model.objects.get(pk=pk)
            self.related_name = request.GET.get('related_name', kwargs.get('related_name'))
            self.model = getattr(self.object, self.related_name).model
        self.list_display = ['id'] + getattr(self.model, 'list_display', [])

        self.paging['page'] = int(request.GET.get('page', 1))
        filters = self.model.get_filters(request)
        self.filters = filters_choices(request, filters, self.model)
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        list_related = getattr(self.model, 'list_related', [])
        queryset = self.model.objects.all()
        if self.object and self.related_name:
            queryset = getattr(self.object, self.related_name).all()
        queryset = queryset.filter(self.model.get_filters_q(self.request)).select_related(*list_related)
        return queryset.distinct()

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

        # TODO: отфильтровать по группам доступа
        if self.model.__name__.lower() == 'servicetimetable':
            _queryset = _queryset.filter(service__in=get_choices(self.request, 'deal.Service', get_list=True))

        elif self.model.__name__.lower() == 'client':
            if (self.request.GET.get('phones') and len(self.request.GET.get('phones')) > 5) or \
                    (self.request.GET.get('full_name') and len(self.request.GET.get('full_name')) > 3):
                pass
            else:
                _queryset = _queryset.filter(
                    Q(rel_deals__deal__branch__in=get_choices(self.request, 'company.Branch', get_list=True)) |
                    Q(rel_deals=None)
                )

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
        if 'view' not in self.permissions:
            return JsonResponse(dict(answer='No permissions'), safe=False)
        if not request.GET:
            return render(request, 'app_vue.jinja2')

        context = dict(
            title=self.model._meta.verbose_name_plural,
            meta_label=self.model._meta.label,
            parent_model_name=self.parent_model.__name__.lower() if self.parent_model else '',
            model_name=self.model.__name__.lower(),
            url=self.request.path,
            actions=self.model.base_actions,
            bread_crumbs=self.object.get_bread_crumbs() if self.object else None,
            child_list=get_child_list(self.object),
            pk=self.object.pk if self.object else '',
            related_name=self.related_name,
            headers=self.model.get_headers(),
            items=self.get_items(),
            count=self.count,
            paging=self.paging,
            permissions=self.permissions,
            filters=self.filters,
        )

        if request.GET.get('debug'):
            from django.shortcuts import render_to_response
            return render_to_response('debug.jinja2', locals())

        return JsonResponse(context)
