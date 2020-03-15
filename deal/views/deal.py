from decimal import Decimal
import json
from datetime import date, datetime, timedelta

from django.db.models import Q
from django.http import JsonResponse
from django.views.generic import ListView
from django.views.generic.edit import View, FormView
from django.shortcuts import render, render_to_response
from django.middleware import csrf
from django.http import HttpResponse, JsonResponse
from django.forms.models import modelform_factory, modelformset_factory, inlineformset_factory
from django.conf import settings

from company.models import Branch, User, TimeTable
from deal.forms import DealForm, DealPersonForm, DealTaskForm
from deal.models import Client, Deal, DealPerson, Stage, Service, ServiceGroup
from identity.forms import PersonFindForm
from identity.models import Person
from mlm.models import Agent, Invite
from sms.views.sms import sms_check_deal
from utils.remote_forms.forms import RemoteForm
from utils.date_time import get_datetime_string, get_date
from utils.normalize_data import normalise_phone, normalise_data


class DealFormView(FormView):
    model = Deal
    branch = None
    service = None
    action = None
    client = None
    deal = None
    deal_form = None
    permissions = []

    def dispatch(self, request, *args, **kwargs):
        self.kwargs.update(kwargs)
        for key, value in self.request.GET.items():
            self.kwargs[key] = value[0] if isinstance(value, list) else value
        for key, value in self.request.POST.items():
            self.kwargs[key] = value[0] if isinstance(value, list) else value

        self.action = self.kwargs.get('action')
        self.permissions = Deal.get_permissions(self.request)
        try:
            self.deal = self.model.objects.get(pk=self.kwargs.get('pk'))
            self.branch = self.deal.branch
        except (Deal.DoesNotExist, ValueError):
            pass
        try:
            self.client = Client.objects.get(pk=request.GET.get('client'))
        except (ValueError, Client.DoesNotExist):
            pass

        if not self.branch:
            try:
                self.branch = Branch.objects.get(pk=(self.request.GET.get('branch') or self.request.POST.get('branch')))
            except Branch.DoesNotExist:
                try:
                    self.branch = self.client.rel_deals.all().exclude(deal__branch=None).last().deal.branch
                except AttributeError:
                    self.branch = User.objects.get(pk=self.request.user.person.id).manager_branches.first() or \
                                  Branch.objects.first()

        return super().dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):
        _kwargs = self.get_form_kwargs()
        _kwargs.update(dict(
            initial=self.kwargs
        ))
        _kwargs['initial'].update(dict(
            branch=self.branch.id,
            request=self.request
        ))
        if _kwargs.get('data'):
            _kwargs['data'] = normalise_data(self.model, _kwargs.get('data'))
            _kwargs['initial'] = normalise_data(self.model, _kwargs.get('initial', {}))
        if self.deal:
            return DealForm(instance=self.deal, **_kwargs)
        return DealForm(**_kwargs)

    @staticmethod
    def get_stages():
        values = ['id', 'step', 'name', 'label', 'color', 'background_color']
        return [step for step in Stage.objects.all().values(*values)]

    def get_person_set(self):
        queryset = DealPerson.objects.none()
        if self.deal:
            queryset = self.deal.rel_persons.all()

        formset_class = modelformset_factory(
            DealPerson,
            form=DealPersonForm,
            fields=DealPersonForm._meta.fields,
            max_num=queryset.count()
        )
        formset = formset_class(queryset=queryset)

        person_data = []
        for form in formset:
            item = form.initial.copy()
            birthday = ''
            if form.instance.person.birthday:
                birthday = form.instance.person.birthday.strftime(settings.DATE_FORMAT)
            item.update(dict(
                id=form.instance.id,
                person_id=form.instance.person.id,
                primary=form.instance.primary,
                full_name=form.instance.person.get_full_name_display(),
                birthday=birthday,
                phone=form.instance.person.get_phone(),
            ))

            person_data.append(item)
        # Если список пуст
        if not person_data:
            person_data = [dict(
                primary=True, control=False, full_name='', phone='', birthday='', email='', contact_type='',
                contact=''
            )]
            if self.kwargs.get('phone'):
                person_data[0].update(phone=self.kwargs.get('phone'))

        if not self.deal and self.client:
            contact = self.client.get_contact()
            person_data = [dict(
                primary=True,
                control=False,
                person_id=self.client.id,
                full_name=self.client.get_full_name_display(),
                birthday=self.client.birthday.strftime(settings.DATE_FORMAT) if self.client.birthday else '',
                phone=self.client.get_phone(),
                email=self.client.get_email(),
                contact_type=contact.type if contact else '',
                contact=contact.value if contact else ''
            )]

        return dict(
            title='Клиент',
            form=modelform_factory(Person, form=DealPersonForm)(),
            data=person_data,
            formset_errors=[],
            errors=dict()
        )

    def post_person_set(self):
        person_set = dict(
            ids_initial=[],
            ids_form=[],
            formset_errors=[],
            errors=dict()
        )
        fields = DealPersonForm._meta.fields
        queryset = self.deal.rel_persons.all() if self.deal else DealPerson.objects.none()
        person_set['ids_initial'] = [i[0] for i in queryset.values_list('id')]
        post_data = {
            'form-TOTAL_FORMS': 0,
            'form-MIN_NUM_FORMS': '',
            'form-MAX_NUM_FORMS': '',
        }
        person_set_data = []
        for i in json.loads(self.request.POST.get('person_set_data', {})):
            i['phone'] = normalise_phone(i.get('phone'))
            person_set_data.append(i)
        post_has_data = False
        post_has_primary = False
        for index, item_data in enumerate(person_set_data):
            post_data['form-TOTAL_FORMS'] += 1
            if item_data.get('id'):
                person_set['ids_form'].append(item_data.get('id'))
            else:
                post_data['form-%s-id' % index] = None
            post_data['form-%s-deal' % index] = self.deal

            for key, value in item_data.items():
                post_data['form-%s-%s' % (index, key)] = value
                if key == 'full_name' and value and not post_has_data:
                    post_has_data = True
                if key == 'primary' and value:
                    post_has_primary = True

        post_data['form-INITIAL_FORMS'] = len(person_set['ids_form'])
        formset_class = modelformset_factory(DealPerson, form=DealPersonForm, fields=fields)
        person_formset = formset_class(data=post_data, queryset=queryset)

        formset_errors = False
        if person_formset.is_valid() and post_has_data and post_has_primary:
            person_set['formset'] = person_formset
        else:
            formset_errors = True
            if not post_has_data:
                person_set['errors']['data'] = 'Необходимы данные о клиенте'
            if not post_has_primary:
                person_set['errors']['primary'] = 'Выберите основного клиента'

        for index in range(0, post_data['form-TOTAL_FORMS']):

            birthday, birthday_error = get_date(post_data['form-%s-birthday' % index])
            if birthday_error:
                formset_errors = True
                person_formset.errors[index]['birthday'] = birthday_error

            # print(post_data['form-%s-full_name' % index], birthday, post_data.get('form-%s-person_id' % index, None))
            if Person.objects.filter(cache__full_name=post_data['form-%s-full_name' % index], birthday=birthday) \
                    .exclude(pk=post_data.get('form-%s-person_id' % index, None)) \
                    .exists():
                formset_errors = True
                person_formset.errors[index]['person_exists'] = 'Клиент с таким Ф.И.О. и днем рождения уже есть'

        person_set['formset_errors'] = person_formset.errors if formset_errors else []
        return person_set

    def save_person_set(self):
        person_set = self.post_person_set()
        person_set['formset'].is_valid()
        person_set['formset'].save()
        person_set['formset'].has_changed()
        deleted = list(set(person_set['ids_initial']) - set(person_set['ids_form']))
        DealPerson.objects.filter(pk__in=deleted).delete()
        return True

    def get_tabs(self):
        tabs = dict(deal=dict(label='Сделка', show=True))

        if self.deal:
            tabs = dict(
                deal=dict(label='Сделка', ids=[], show=True),
                clients=dict(label='Клиенты', ids=[], show=False),
                tasks=dict(label='Задачи', ids=[], show=False),
                comments=dict(label='Комментарии', ids=[], show=False),
                sms=dict(label='Смс', ids=[], show=False),
                history=dict(label='История', ids=[], show=False),
            )
            tabs['sms']['ids'] += [i['id'] for i in self.deal.sms.all().values('id')]
            for rel_person in self.deal.rel_persons.all():
                tabs['clients']['ids'].append(rel_person.person.id)
                tabs['tasks']['ids'] += [i['id'] for i in rel_person.deal.tasks.all().values('id')]
                tabs['tasks']['ids'] += [i['id'] for i in rel_person.person.tasks.all().values('id')]

                tabs['comments']['ids'] += [i['id'] for i in rel_person.person.comments.all().values('id')]
                for rel_person_deal in rel_person.person.rel_deals.all():
                    tabs['comments']['ids'] += [i['id'] for i in rel_person_deal.deal.comments.all().values('id')]

            for key, tab in tabs.items():
                tab['ids'] = list(set(tab['ids']))
                tab['label'] = '%s (%s)' % (tab['label'], len(tab['ids'])) if tab['ids'] else tab['label']

        return tabs

    def post(self, request, *args, **kwargs):
        self.action = 'change' if self.action == 'save' else self.action
        if self.action not in self.permissions:
            return HttpResponse('no permissions')

        if self.action == 'delete':
            self.deal.delete()
            return HttpResponse('ok')
        else:
            self.deal_form = self.get_form()
            person_set = self.post_person_set()
            if self.deal_form.is_valid() \
                    and not person_set['errors'] \
                    and person_set.get('formset') and not person_set['formset_errors']:
                self.deal_form.save(commit=False)
                self.deal = self.deal_form.instance
                self.save_person_set()
                sms_check_deal(self.deal)
                self.deal_form.save()
                return JsonResponse(dict(
                    tabs=self.get_tabs(),
                    id=self.deal_form.instance.id,
                    title=self.deal_form.instance.cache.get('title', ''),
                    stage=self.deal_form.instance.stage.id,
                    message=dict(type='success', text='Сохранено')
                ))

            return JsonResponse(dict(
                form=dict(errors=self.deal_form.errors),
                person_set=dict(
                    errors=person_set['errors'],
                    formset_errors=person_set['formset_errors']
                )
            ))

    def get(self, request, *args, **kwargs):
        if 'view' not in self.permissions:
            return JsonResponse(dict(answer='No permissions'), safe=False)
        if not request.GET:
            return render(request, 'app_vue.jinja2')

        person_set = self.get_person_set()
        person_set['form'] = RemoteForm(person_set['form']).as_dict()
        person_set['search'] = dict()

        form = RemoteForm(self.get_form(), model=self.model, csrf_token=csrf.get_token(self.request)).as_dict()
        if self.branch.periodic:
            form['fields']['services']['widget']['choices'] = [
                dict(label="Правка", value=1),
                dict(label="Диагностика", value=3)
            ]
        if not form['data']['services']:
            form['data']['services'] = [1]

        context = dict(
            title=self.deal.cache.get('title', None) if self.deal else 'Новая сделка',
            id=self.deal.id if self.deal else None,
            form=form,
            person_set=person_set,
            # person_find_form=dict(RemoteForm(PersonFindForm(), csrf_token=csrf.get_token(self.request)).as_dict()),
            stages=self.get_stages(),
            tabs=self.get_tabs(),
            permissions=self.permissions
        )

        if self.request.GET.get('debug'):
            return render_to_response('debug.jinja2', locals())

        return JsonResponse(context)


class DealCostView(View):
    data = dict()
    agent = None
    cost = Decimal('0.00')

    def dispatch(self, request, *args, **kwargs):
        today = datetime.now()
        self.data = self.request.POST.dict()
        master = self.data.get('master')
        services = json.loads(self.data.get('services'))
        if master and services:
            service_set = Service.get_cost(master, services)
            try:
                self.agent = Agent.objects.get(pk=self.data.get('mlm_agent'))
            except (ValueError, TypeError, Agent.DoesNotExist):
                pass

            for person in json.loads(self.data.get('person_set_data')):
                if person['control']:
                    continue
                try:
                    age = (today - datetime.strptime(person['birthday'], '%d.%m.%Y')).days / 365
                except (TypeError, ValueError):
                    age = None
                cost_key = 'cost' if not age or age > 14 else 'cost_kid'
                for service in service_set:
                    self.cost += service[cost_key]
        else:
            self.cost = Decimal('0.00')

        return super().dispatch(request, *args, **kwargs)

    def get_discount(self):
        if self.agent:
            cost = Decimal(self.cost - (self.cost / 100 * self.agent.discount))
            return round(cost, 2)
        return self.cost

    def post(self, request, *args, **kwargs):
        if self.agent:
            self.cost = self.get_discount()
        return JsonResponse(dict(
            cost=str(self.cost),
        ))
