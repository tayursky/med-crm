import json

from django.views.generic.edit import FormView
from django.forms.models import modelform_factory, modelformset_factory, inlineformset_factory
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.middleware import csrf
from django.urls import reverse, reverse_lazy

from utils.remote_forms.forms import RemoteForm
from utils.normalize_data import normalise_data
from utils.choices import get_choices
from deal.forms import *
from deal.models import *
from directory.models import *
from directory.utils import get_model, get_linked_obj, get_detail_fields_mapping, get_child_list
from directory.forms import DirectoryForm
from identity.models import Person
from sms.models import Sms


class ModelActions(FormView):
    model = None
    action = None
    parents = []
    object = None
    formset_errors = dict()
    permissions = []

    def dispatch(self, request, *args, **kwargs):
        self.model = get_model(self.kwargs.get('model_name'))
        self.permissions = self.model.get_permissions(request)

        if 'view' not in self.permissions:
            return JsonResponse(dict(answer='No permissions'), safe=False)
        self.formset_errors = dict()
        self.action = kwargs.get('action', None)
        self.kwargs.update(kwargs)
        if request.method == 'GET':
            for key, value in self.request.GET.items():
                self.kwargs[key] = value[0] if isinstance(value, list) else value
        self.parents = getattr(self.model, 'list_parents', [])
        if self.kwargs.get('related_name'):
            self.kwargs.update({
                'model': self.model
            })

            for parent in self.parents:
                if self.request.GET.get(parent):
                    self.kwargs.update({parent: self.request.GET.get(parent)})
                    print('PARENT', parent, self.request.GET.get(parent))

        if kwargs.get('pk'):
            self.object = self.model.objects.get(pk=kwargs['pk'])

        if self.model._meta.label == 'company.Branch':
            if self.object.id in get_choices(self.request, 'company.Branch', True):
                self.permissions += ['change', 'view', 'add']

        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self, **kwargs):
        return 'get_success_url'

    def get_form(self, form_class=None):
        fields = getattr(self.model, 'list_form_fields', [])
        kwargs = self.get_form_kwargs()
        kwargs.update(dict(
            initial=self.kwargs,
        ))

        # TODO: initial from request.GET
        get_initial = json.loads(self.request.GET.get('initial', '{}'))
        for k, v in get_initial.items():
            try:
                kwargs['initial'][k] = int(v)
            except:
                kwargs['initial'][k] = v

        if not form_class:
            try:
                form_class = eval("%sForm" % self.model.__name__)
            except NameError:
                form_class = modelform_factory(self.model, form=DirectoryForm, fields=fields)

        if 'data' in kwargs:
            kwargs['data'] = normalise_data(self.model, kwargs['data'])

        if self.object:
            return form_class(instance=self.object, **kwargs)
        return form_class(**kwargs)

    def get_formset(self):
        formset_list = []
        formset = dict()
        for formset_name in getattr(self.model, 'list_formset', []):
            formset_list.append(formset_name)
            model = getattr(self.model, formset_name).rel.related_model
            fields = getattr(model, 'list_form_fields', [])

            queryset = model.objects.none()
            if self.object:
                queryset = getattr(self.object, formset_name).all()

            formset_class = modelformset_factory(
                model,
                fields=model.list_form_fields,
                max_num=queryset.count()
            )
            data = []
            for form in formset_class(queryset=queryset):
                item = RemoteForm(form, model=model).as_dict()['data']
                item['id'] = form.instance.id
                if form.Meta.model._meta.verbose_name == 'Семейные связи':
                    item['relative'] = Person.objects.get(pk=item['relative']).__str__()
                data.append(item)

            # deal.Client.phone
            if self.kwargs.get('phone') and self.model._meta.label == 'deal.Client' \
                    and formset_name == 'phones' and not data:
                data = [{'value': self.kwargs.get('phone'), 'type': 1}]

            formset[formset_name] = dict(
                name=formset_name,
                label=model._meta.verbose_name_plural,
                form=RemoteForm(modelform_factory(model, form=DirectoryForm, fields=fields)()).as_dict(),
                data=data,
            )
        return formset_list, formset

    def post_formset(self):
        formset = dict()
        for formset_name in getattr(self.model, 'list_formset', []):
            formset[formset_name] = dict(
                ids_initial=[],
                ids_form=[]
            )
            model = getattr(self.model, formset_name).rel.related_model
            fields = getattr(model, 'list_form_fields', [])
            parent_rel = getattr(model, 'parent_rel', None)
            queryset = model.objects.none()
            if self.object:
                queryset = getattr(self.object, formset_name).all()
                fields.append(parent_rel)
            elif parent_rel in fields:
                fields.remove(parent_rel)

            formset[formset_name]['ids_initial'] = [i[0] for i in queryset.values_list('id')]
            _data = {
                'form-TOTAL_FORMS': 0,
                'form-MIN_NUM_FORMS': '',
                'form-MAX_NUM_FORMS': '',
            }
            formset_post = json.loads(self.request.POST.get('formset', {}))
            for index, item_data in enumerate(formset_post[formset_name]):
                _data['form-TOTAL_FORMS'] += 1
                if item_data.get('id'):
                    formset[formset_name]['ids_form'].append(item_data.get('id'))
                else:
                    _data['form-%s-id' % index] = None
                for key, value in item_data.items():
                    _data['form-%s-%s' % (index, key)] = value
                if self.object:
                    _data['form-%s-%s' % (index, parent_rel)] = self.object.id

            _data['form-INITIAL_FORMS'] = len(formset[formset_name]['ids_form'])
            formset_class = modelformset_factory(model, fields=fields)
            formset_result = formset_class(data=_data, queryset=queryset)

            if formset_result.is_valid():
                formset[formset_name]['formset'] = formset_result
            else:
                self.formset_errors[formset_name] = formset_result.errors
        return formset

    def save_formset(self, form, formset):
        index = 0
        for formset_name, item in formset.items():
            rel = getattr(form.instance, formset_name)

            item['formset'].save()
            deleted = list(set(item['ids_initial']) - set(item['ids_form']))
            rel.filter(id__in=deleted).delete()
            # rel.add(*item['formset'].new_objects)
            # rel.remove(*deleted)
            # rel.model.objects.filter(pk__in=deleted).delete()
            index += 1
        return True

    def post(self, request, *args, **kwargs):
        self.action = 'change' if self.action == 'save' else self.action
        if self.action not in self.permissions:
            return HttpResponse('no perm')

        if self.action == 'delete':
            self.object.delete()
            context = dict(
                deleted=True,
                message=dict(type='success', text='Удалено'),
            )
            return JsonResponse(context)

        form = self.get_form()
        formset = self.post_formset()
        if form.is_valid() and not self.formset_errors:
            form.save()
            self.object = form.instance
            formset = self.post_formset()  # При сохранении нового объекта, нужно получить formset с self.object
            self.save_formset(form, formset)
            context = dict(
                id=self.object.id,
                message=dict(type='success', text='Сохранено')
            )
            return JsonResponse(context)
        else:
            return self.form_invalid(form)

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

    def get_tabs(self):
        title = 'Карточка клиента'

        if not self.object and self.model._meta.label == 'deal.Client':
            return title, None
        elif not self.object or not self.model._meta.label == 'deal.Client':
            return None, None

        tabs = dict(deal=dict(label='Сделка', show=True))

        if self.object and self.model._meta.label == 'deal.Client':
            tabs = dict(
                client=dict(label='Персональные данные', ids=[], show=True),
                deals=dict(label='Сделки', ids=[], show=False),
                tasks=dict(label='Задачи', ids=[], show=False),
                comments=dict(label='Комментарии', ids=[], show=False),
                sms=dict(label='Смс', ids=[], show=False),
                history=dict(label='История', ids=[], show=False),
            )
            tabs['sms']['ids'] += [i['id'] for i in Sms.objects.filter(person=self.object).values('id')]
            for rel_deal in self.object.rel_deals.all():
                tabs['deals']['ids'].append(rel_deal.id)
                tabs['tasks']['ids'] += [i['id'] for i in rel_deal.deal.tasks.all().values('id')]
                tabs['comments']['ids'] += [i['id'] for i in rel_deal.deal.comments.all().values('id')]
            tabs['comments']['ids'] += [i['id'] for i in self.object.comments.all().values('id')]
            tabs['tasks']['ids'] += [i['id'] for i in self.object.tasks.all().values('id')]
            for key, tab in tabs.items():
                tab['label'] = '%s (%s)' % (tab['label'], len(tab['ids'])) if tab['ids'] else tab['label']

            title = self.object.cache['full_name']
        return title, tabs

    def render_to_response(self, context, **response_kwargs):
        if 'view' not in self.permissions:
            return HttpResponse('no perm')
        formset_list, formset = self.get_formset()
        _form = RemoteForm(self.get_form(), model=self.model, csrf_token=csrf.get_token(self.request)).as_dict()

        # TODO: отфильтровать по группам доступа
        if self.model.__name__.lower() == 'expense':
            _form['fields']['branch']['widget']['choices'] = get_choices(self.request, 'company.Branch')
        elif self.model.__name__.lower() == 'servicetimetable':
            _form['fields']['service']['widget']['choices'] = get_choices(self.request, 'deal.Service')

        title, tabs = self.get_tabs()

        if self.get_form().is_valid() and not self.formset_errors:
            message = dict(type='success', text='Сохранено')
        else:
            message = dict(type='warning', text='Ошибка')

        context = dict(
            title=title,
            tabs=tabs,
            parents=self.parents,
            form=_form,
            formset_list=formset_list,
            formset=formset,
            formset_errors=self.formset_errors,
            message=message,
            permissions=self.permissions
        )

        if self.request.GET.get('debug'):
            from django.shortcuts import render_to_response
            return render_to_response('debug.jinja2', locals())

        return JsonResponse(context)
