import json
from django.core import serializers
from django.contrib.auth.models import Group, Permission
from django.urls import reverse, reverse_lazy
from django.http import HttpResponse, JsonResponse
from django.views.generic import DetailView, ListView, TemplateView, View
from django.views.generic.edit import FormView
from django.forms.models import modelform_factory
from django.middleware import csrf
from django.shortcuts import render, render_to_response, get_object_or_404

from company.models import User, UserGroup
from directory.forms import DirectoryForm, FilterForm
from utils.remote_forms.forms import RemoteForm
from utils.decorators.permission import perm_required


class GroupListView(ListView):
    model = UserGroup
    list_display = None
    count = 0
    paging = dict(
        range=9,
        page_items=20,
        page=1,
        pages=1
    )
    filters = {}

    @perm_required('company.view_usergroup')
    def dispatch(self, request, *args, **kwargs):
        self.list_display = ['id'] + getattr(self.model, 'list_display', [])
        self.paging['page'] = int(request.GET.get('page', 1))
        # self.filters = self.get_filters(request)
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        list_related = getattr(self.model, 'list_related', [])  # поля требующие select_related
        queryset = self.model.objects.all() \
            .select_related(*list_related)
        # queryset = queryset.filter(self.q_filters)
        return queryset

    def get_items(self):
        items = []
        self.count = self.get_queryset().count()
        self.paging['pages'] = round(self.count / self.paging['page_items'] + 0.5)
        begin = (self.paging['page'] - 1) * self.paging['page_items']
        for q_item in self.get_queryset()[begin:begin + self.paging['page_items']]:
            item = dict()
            for field_name in self.list_display:
                _q_item = q_item
                for field in field_name.split('__'):
                    try:
                        _q_item = getattr(q_item, 'get_%s_display' % field)()
                    except AttributeError:
                        _q_item = getattr(_q_item, field)
                item[field_name] = _q_item.__str__() if _q_item else ''
            items.append(item)
        return items

    def get(self, request, *args, **kwargs):
        if not request.GET:
            return render(request, 'app_vue.jinja2')

        context = dict(
            title=self.model._meta.verbose_name_plural,
            url=self.request.path,
            model_name=self.model.__name__.lower(),
            actions=self.model.base_actions,
            headers=self.model.get_headers(),
            filters=self.filters,
            items=self.get_items(),
            count=self.count,
            paging=self.paging
        )

        if request.GET.get('debug'):
            from django.shortcuts import render_to_response
            return render_to_response('debug.jinja2', locals())

        return JsonResponse(context)


class GroupView(FormView):
    model = UserGroup
    action = None
    group = None

    @perm_required('company.view_usergroup')
    def dispatch(self, request, *args, **kwargs):
        self.action = kwargs.get('action', None)
        self.kwargs.update(kwargs)
        if request.method == 'GET':
            for key, value in self.request.GET.items():
                self.kwargs[key] = value[0] if isinstance(value, list) else value
        try:
            self.group = self.model.objects.get(pk=kwargs['pk'])
        except ValueError:
            pass

        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self, **kwargs):
        return 'get_success_url'

    def get_form(self, form_class=None):
        fields = getattr(self.model, 'list_form_fields', [])
        kwargs = self.get_form_kwargs()
        kwargs.update({
            'initial': self.kwargs
        })

        if not form_class:
            try:
                form_class = eval("%sForm" % self.model.__name__)
            except NameError:
                form_class = modelform_factory(self.model, form=DirectoryForm, fields=fields)

        if self.group:
            return form_class(instance=self.group, **kwargs)
        return form_class(**kwargs)

    def get_perms(self):
        perms = []
        content_type_list = ['company', 'deal', 'directory', 'identity', 'sip', 'mlm']
        group_perms = [i['id'] for i in self.group.permissions.all().values('id')] if self.group else []
        for permission in Permission.objects.filter(content_type__app_label__in=content_type_list):
            # print(permission.content_type.name[:10])
            if permission.content_type.name[:10] != 'historical':
                perms.append(dict(
                    id=permission.id,
                    app_label=permission.content_type.app_label,
                    model=permission.content_type.model,
                    content_type=permission.content_type.name,
                    name=permission.name,
                    codename=permission.codename,
                ))

        return perms, group_perms

    def post(self, request, *args, **kwargs):
        if self.action == 'delete':
            self.group.delete()
            return JsonResponse(dict(
                message=dict(type='success', text='Удалено'),
                url=reverse_lazy('company:group_list')
            ))
        else:
            form = self.get_form()
            if form.is_valid():
                form.save()
                # Url redirect for new instance
                url = reverse_lazy('company:group_view', kwargs={'pk': form.instance.id}) if not self.group else None
                self.group = form.instance

                groups_perms = json.loads(self.request.POST.get('group_perms', {}))
                self.group.permissions.clear()
                self.group.permissions.add(*groups_perms)

                context = dict(
                    message=dict(type='success', text='Сохранено'),
                    url=url
                )
                return JsonResponse(context)
            else:
                return JsonResponse(dict(
                    errors=form.errors,
                ))

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context.update({
            'url': self.request.path,
            'title': self.model._meta.verbose_name,
            'model_name': self.model.__name__.lower(),
            'error': [],
            'success_url': self.success_url
        })
        return context

    def get(self, request, *args, **kwargs):
        perms, group_perms = self.get_perms()
        context = dict(
            form=RemoteForm(self.get_form(), model=self.model, csrf_token=csrf.get_token(self.request)).as_dict(),
            perms=perms,
            group_perms=group_perms,
        )
        if self.request.GET.get('debug'):
            return render_to_response('debug.jinja2', locals())
        return JsonResponse(context, safe=False)
