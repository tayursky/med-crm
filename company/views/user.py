import json

from django.views.generic import ListView
from django.views.generic.edit import FormView
from django.forms.models import modelform_factory, modelformset_factory
from django.http import JsonResponse
from django.middleware import csrf

from django.shortcuts import render_to_response
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from directory.forms import DirectoryForm, FilterForm
from company.forms import UserForm
from company.models import User, UserGroup

from utils.decorators.permission import perm_required
from utils.remote_forms.forms import RemoteForm
from utils.choices import get_choices, filters_choices
from utils.word import get_translit
from identity.models import Person, Account
from identity.forms import PersonFindForm


class UserListView(ListView):
    object = None
    related_name = None
    list_display = None
    count = 0
    paging = dict(
        range=9,
        page_items=20,
        page=1,
        pages=1
    )
    filters = {}

    @perm_required('company.view_user')
    def dispatch(self, request, *args, **kwargs):
        self.model = User
        self.list_display = ['id'] + getattr(self.model, 'list_display', [])
        self.paging['page'] = int(request.GET.get('page', 1))
        filters = self.model.get_filters(request)
        self.filters = filters_choices(request, filters, self.model)
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        list_related = getattr(self.model, 'list_related', [])  # поля требующие select_related
        queryset = self.model.objects.all()
        if self.object and self.related_name:
            queryset = getattr(self.object, self.related_name).all()
        queryset = queryset.filter(self.model.get_filters_q(self.request)).select_related(*list_related)
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


class UserView(LoginRequiredMixin, FormView):
    model = User
    action = None
    person = None
    user = None
    formset_errors = dict()
    permissions = []

    @perm_required('company.view_user')
    def dispatch(self, request, *args, **kwargs):
        self.permissions = self.model.get_permissions(request)
        self.formset_errors = dict()
        self.kwargs.update(kwargs)
        self.action = self.kwargs.get('action', None)
        if request.method == 'GET':
            for key, value in self.request.GET.items():
                self.kwargs[key] = value[0] if isinstance(value, list) else value

        try:
            self.user = self.model.objects.get(pk=self.kwargs['pk'])
        except (ValueError, User.DoesNotExist):
            pass

        return super().dispatch(request, *args, **kwargs)

    def create_user_from_person(self):
        self.person = Person.objects.get(pk=self.kwargs.get('pk'))
        if self.person.account:
            self.person.account.is_staff=True
            self.person.account.save()
            return JsonResponse(dict(user=self.person.id), safe=False)

        username = None
        count = 0
        while not username or Account.objects.filter(username=username).exists():
            count += 1
            if username:
                username += str(count)
            else:
                username = '%s_%s%s' % (get_translit(self.person.last_name),
                                        get_translit(self.person.first_name[0]),
                                        get_translit(self.person.patronymic[0]) if self.person.patronymic else '',
                                        )
        print(username)
        account = Account.objects.create(
            username=username,
            email=self.person.get_email(),
            is_staff=True,
            is_active=True
        )
        self.person.account = account
        self.person.save()
        self.user = self.model.objects.filter(account=account).first()
        return JsonResponse(dict(user=self.user.id), safe=False)

    def get_success_url(self, **kwargs):
        return 'get_success_url'

    def get_form(self, form_class=UserForm):
        # fields = getattr(self.model, 'list_form_fields', [])
        kwargs = self.get_form_kwargs()
        kwargs.update(dict(initial=self.kwargs))
        if self.user:
            return form_class(instance=self.user, **kwargs)
        return form_class(**kwargs)

    def get_formset(self):
        formset_list = []
        formset = dict()
        for formset_name in getattr(self.model, 'list_formset', []):
            formset_list.append(formset_name)
            model = getattr(self.model, formset_name).rel.related_model
            fields = getattr(model, 'list_form_fields', [])
            queryset = model.objects.none()
            if self.user:
                queryset = getattr(self.user, formset_name).all()

            formset_class = modelformset_factory(
                model,
                fields=model.list_form_fields,
                max_num=queryset.count()
            )
            data = []
            for form in formset_class(queryset=queryset):
                item = form.initial.copy()
                item['id'] = form.instance.id
                data.append(item)

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
            queryset = model.objects.none()
            parent_rel = getattr(model, 'parent_rel', None)
            if self.user:
                queryset = getattr(self.user, formset_name).all()
                fields.append(parent_rel)
            else:
                while parent_rel in fields:
                    fields.remove(parent_rel)

            # print('parent_rel', parent_rel)
            # import ipdb; ipdb.set_trace()

            formset[formset_name]['ids_initial'] = [i[0] for i in queryset.values_list('id')]
            post_data = {
                'form-TOTAL_FORMS': 0,
                'form-MIN_NUM_FORMS': '',
                'form-MAX_NUM_FORMS': '',
            }
            formset_post = json.loads(self.request.POST.get('formset', {}))
            for index, item_data in enumerate(formset_post[formset_name]):
                post_data['form-TOTAL_FORMS'] += 1
                if item_data.get('id'):
                    formset[formset_name]['ids_form'].append(item_data.get('id'))
                else:
                    post_data['form-%s-id' % index] = None
                for key, value in item_data.items():
                    post_data['form-%s-%s' % (index, key)] = value

                try:
                    post_data['form-%s-%s' % (index, parent_rel)] = self.user.id
                except AttributeError:
                    post_data.pop('form-%s-%s' % (index, parent_rel), None)

            post_data['form-INITIAL_FORMS'] = len(formset[formset_name]['ids_form'])

            formset_class = modelformset_factory(model, fields=fields)
            formset_result = formset_class(data=post_data, queryset=queryset)

            if formset_result.is_valid():
                formset[formset_name]['formset'] = formset_result
            else:
                self.formset_errors[formset_name] = formset_result.errors
        return formset

    def save_formset(self, form, formset):
        for formset_name, item in formset.items():
            item['formset'].save()
            rel = getattr(form.instance, formset_name)
            deleted = list(set(item['ids_initial']) - set(item['ids_form']))
            rel.filter(id__in=deleted).delete()
            # rel.add(*item['formset'].new_objects)
        return True

    def get_groups(self, *args, **kwargs):
        groups = dict()
        groups_ordered = []
        user_groups = []
        for group in UserGroup.objects.all().values('id', 'name'):
            groups[group['id']] = group['name']
            groups_ordered.append(group['id'])
        if self.user and self.user.account:
            user_groups = [i['id'] for i in self.user.account.groups.all().values('id')]
        return dict(
            all=groups,
            groups_ordered=groups_ordered,
            user_groups=user_groups,
        )

    def post(self, request, *args, **kwargs):
        if self.action == 'delete':
            self.user.account.delete()
            self.user.delete()
            return JsonResponse(dict(
                message=dict(type='success', text='Удалено'),
                url=reverse_lazy('company:user_list')
            ))
        else:
            form = self.get_form()
            formset = self.post_formset()
            if form.is_valid() and not self.formset_errors:
                form.save()
                url = reverse_lazy('company:user_view', kwargs={'pk': form.instance.id}) if not self.user else None
                self.user = form.instance
                formset = self.post_formset()
                self.save_formset(form, formset)
                user_groups = json.loads(self.request.POST.get('groups', {}))
                self.user.account.groups.clear()
                self.user.account.groups.add(*user_groups)

                context = dict(
                    message=dict(type='success', text='Сохранено'),
                    url=url
                )
                return JsonResponse(context)
            else:
                return JsonResponse(dict(
                    errors=form.errors,
                    formset_errors=self.formset_errors,
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

        if self.kwargs.get('create_from_person'):
            return self.create_user_from_person()

        formset_list, formset = self.get_formset()
        context = dict(
            person_find_form=dict(RemoteForm(PersonFindForm(), csrf_token=csrf.get_token(self.request)).as_dict()),
            form=RemoteForm(self.get_form(), model=self.model, csrf_token=csrf.get_token(self.request)).as_dict(),
            formset_list=formset_list,
            formset=formset,
            formset_errors=self.formset_errors,
            groups=self.get_groups(),
            permissions=self.permissions
        )
        if self.request.GET.get('debug'):
            return render_to_response('debug.jinja2', locals())
        return JsonResponse(context, safe=False)
