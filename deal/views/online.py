import calendar
import decimal
import math
import json
from datetime import date, datetime, timedelta

from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from openpyxl.writer.excel import save_virtual_workbook
from openpyxl.styles import PatternFill, Border, Side, Alignment, Protection, Font, Side
from openpyxl.formatting.rule import ColorScaleRule, CellIsRule, FormulaRule

from django.http import HttpResponse, JsonResponse
from django.views.generic.edit import View, FormView
from django.utils.http import urlquote
from django.utils.translation import ugettext as _
from django.shortcuts import render, redirect, render_to_response
from django.middleware import csrf
from django.forms.models import modelform_factory, modelformset_factory, inlineformset_factory

from deal.forms import OnlineDealForm, OnlineDealPersonForm
from deal.models import Deal, Service, DealPerson
from deal.views.deal_calendar import DealCalendar
from identity.models import Person
from utils.date_time import delta_minutes, get_week_start
from utils.remote_forms.forms import RemoteForm
from utils.normalize_data import normalise_phone


class OnlineView(DealCalendar, FormView):
    """
        Запись онлайн
    """
    deal = None
    day_start = None
    day_finish = None
    timezone = 0
    action = None
    show = True
    next = True

    def dispatch(self, request, *args, **kwargs):
        self.service, self.service_set = self.set_service()
        self.timezone = self.service.branch.city.timezone
        self.timing_exclude = []
        self.action = kwargs.get('action')
        try:
            self.day_start = datetime.strptime(request.GET.get('day'), '%d.%m.%Y')
        except TypeError:
            pass

        get_day = request.GET.get('get_day')
        if not self.day_start or get_day == 'tomorrow':
            self.day_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)

        if get_day == 'prev':
            self.day_start -= timedelta(days=1)
        elif get_day == 'next':
            self.day_start += timedelta(days=1)

        self.day_finish = self.day_start + timedelta(hours=24)
        self.deals = self.get_deals()
        self.show = self.day_start > datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        self.next = self.day_start > datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) \
                    + timedelta(days=1)
        return super().dispatch(request, *args, **kwargs)

    def set_service(self):
        service = None
        service_set = dict(timezone=0)
        try:
            service = Service.objects.get(pk=(self.request.GET.get('service') or self.request.POST.get('service')))
        except Service.DoesNotExist:
            service = Service.objects.first()

        if service:
            service_set = dict(
                id=service.id,
                name=service.name,
                interval=service.interval_time.hour * 60 + service.interval_time.minute,
                timezone=service.branch.city.timezone
            )
        return service, service_set

    def get_deals(self):
        deal_queryset = Deal.objects.filter(
            service=self.service,
            start_datetime__gte=self.day_start,
            start_datetime__lte=self.day_finish + timedelta(hours=1),
            step__number__gt=0
        )
        deals = dict()
        values = ['id', 'service__id', 'step__id', 'step__step', 'cost', 'start_datetime', 'finish_datetime']
        for deal in deal_queryset:  # .values(*values):
            deal.start_datetime += timedelta(hours=self.timezone)
            deal.finish_datetime += timedelta(hours=self.timezone)

            start = int(deal.start_datetime.strftime('%Y%m%d%H%M'))
            finish = int(deal.finish_datetime.strftime('%Y%m%d%H%M'))
            deals[start] = dict(
                step=deal.step_id,
                step_number=deal.step.number,
                step_name=deal.step.name,
                step_label=deal.step.label,
                start=start,
                start_string=deal.start_datetime.strftime('%H:%M'),
                finish=finish,
                finish_string=deal.finish_datetime.strftime('%H:%M'),
                minutes=delta_minutes(start, finish),
            )
        return deals

    def get_day_set(self):
        title = '{day} {month} {year}'.format(
            day=self.day_start.strftime('%d'),
            month=_(self.day_start.strftime('%B')).lower(),
            year=self.day_start.strftime('%Y'),
        )
        return dict(
            title=title,
            year=self.day_start.year,
            month=self.day_start.month,
            label=self.day_start.strftime('%d.%m.%Y'),
            key=self.day_start.strftime('%Y%m%d'),
            timing=self.get_day_timing(self.deals, self.day_start),
            timing_exclude=self.timing_exclude
        )

    def get_person_set(self):
        queryset = DealPerson.objects.none()
        formset_class = modelformset_factory(
            DealPerson,
            form=OnlineDealPersonForm,
            fields=OnlineDealPersonForm._meta.fields,
            max_num=queryset.count()
        )
        formset = formset_class(queryset=queryset)

        person_data = []
        for form in formset:
            item = form.initial.copy()
            item.update(dict(
                id=form.instance.id,
                person_id=form.instance.person.id,
                primary=form.instance.primary,
                full_name=form.instance.person.get_full_name_display(),
                phone=None, email=None,
            ))
            # print(item)
            # item['phone'] = item['phone'].national_number

            person_data.append(item)
        # Если список пуст
        person_data = person_data or [dict(
            primary=True,
            control=False,
            first_name='',
            last_name='',
            patronymic='',
            birthday='',
            phone='',
            email='',
        )]

        return dict(
            title='Человек',
            form=modelform_factory(Person, form=OnlineDealPersonForm)(),
            data=person_data,
            formset_errors=[],
            errors=dict()
        )

    def get_form(self, form_class=None):
        kwargs = self.get_form_kwargs()
        kwargs.update({
            'initial': self.kwargs
        })
        kwargs['initial']['service'] = self.service.id
        return OnlineDealForm(**kwargs)

    def post_person_set(self):
        person_set = dict(
            ids_initial=[],
            ids_form=[],
            formset_errors=[],
            errors=dict()
        )
        fields = OnlineDealPersonForm._meta.fields
        queryset = DealPerson.objects.none()
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
        # print('person_set_data', person_set_data)
        for index, item_data in enumerate(person_set_data):
            post_data['form-TOTAL_FORMS'] += 1
            if item_data.get('id'):
                person_set['ids_form'].append(item_data.get('id'))
            else:
                post_data['form-%s-id' % index] = None

            post_data['form-%s-deal' % index] = self.deal

            for key, value in item_data.items():
                post_data['form-%s-%s' % (index, key)] = value
                if value and not post_has_data:
                    post_has_data = True
                if key == 'primary' and value:
                    post_has_primary = True

        post_data['form-INITIAL_FORMS'] = len(person_set['ids_form'])
        formset_class = modelformset_factory(DealPerson, form=OnlineDealPersonForm, fields=fields)
        person_formset = formset_class(data=post_data, queryset=queryset)

        if person_formset.is_valid() and post_has_data and post_has_primary:
            person_set['formset'] = person_formset
        else:
            if not post_has_primary:
                person_set['errors']['primary'] = 'Выберите основного клиента'
            if not post_has_data:
                person_set['errors']['data'] = 'Необходимы данные о клиенте'
            if not person_formset.is_valid():
                person_set['formset_errors'] = person_formset.errors

        return person_set

    def save_person_set(self):
        person_set = self.post_person_set()
        person_set['formset'].is_valid()
        person_set['formset'].save()
        person_set['formset'].has_changed()
        deleted = list(set(person_set['ids_initial']) - set(person_set['ids_form']))
        DealPerson.objects.filter(pk__in=deleted).delete()
        return True

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        person_set = self.post_person_set()
        if form.is_valid() and not person_set['errors'] and not person_set['formset_errors']:
            form.save()
            self.deal = form.instance
            self.save_person_set()
            return HttpResponse('ok')

        return JsonResponse(dict(
            form=dict(errors=form.errors),
            person_set=dict(
                errors=person_set['errors'],
                formset_errors=person_set['formset_errors']
            )
        ))

    def get(self, request, *args, **kwargs):
        if not request.GET:
            return render(request, 'app_vue.jinja2')

        person_set = self.get_person_set()
        person_set['form'] = RemoteForm(person_set['form']).as_dict()

        context = dict(
            title='Онлайн запись',
            service_set=self.service_set,
            day_set=self.get_day_set(),
            form=RemoteForm(self.get_form(), model=Deal, csrf_token=csrf.get_token(self.request)).as_dict(),
            person_set=person_set,
            next=self.next
        )
        if self.show:
            context.update(dict(
                deals=self.deals,
                timing=self.get_range(self.day_start),
            ))

        if self.request.GET.get('debug'):
            return render_to_response('debug.jinja2', locals())
        return JsonResponse(context, safe=False)
