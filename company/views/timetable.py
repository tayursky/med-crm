import calendar
import decimal
import json
from datetime import date, datetime, timedelta

from django.db.models import Q
from django.views.generic import View, ListView
from django.views.generic.edit import FormView
from django.utils.translation import ugettext as _
from django.http import HttpResponse, JsonResponse
from django.middleware import csrf
from django.shortcuts import render, render_to_response
from django.forms.models import modelform_factory, modelformset_factory, inlineformset_factory
from django.views.decorators.csrf import csrf_exempt

from absolutum.mixins import CoreMixin
from absolutum.settings import DATETIME_FORMAT, TIME_FORMAT
from company.forms import TimeTableForm
from company.models import Branch, User, TimeTable
from deal.models import Deal, Service
from directory.forms import DirectoryForm
from identity.models import Person
from identity.utils import LoginRequiredMixin
from utils.date_time import delta_minutes
from utils.choices import filters_choices, get_choices
from utils.remote_forms.forms import RemoteForm
from utils.normalize_data import normalise_data


class TimeTableList(LoginRequiredMixin, View, CoreMixin):
    """
        Табель учета рабочего времени
    """
    model = TimeTable
    branch = None
    filters = dict()
    filters_q = Q()
    timezone = 0
    work_shifts = dict()
    year = None
    month = None
    start_month = None
    end_month = None
    workers = None
    start_time = '10:00'
    end_time = '19:00'
    permissions = []

    def dispatch(self, request, *args, **kwargs):
        self.permissions = self.model.get_permissions(self.request)
        if not request.GET.get('branch'):
            request.GET._mutable = True
            if not self.request.user.has_perm('Администраторы'):
                request.GET['branch'] = User.objects.get(pk=request.user.person.id).manager_branches.first().id
            else:
                request.GET['branch'] = Branch.objects.first().id
        self.branch = Branch.objects.get(pk=request.GET.get('branch'))
        self.timezone = self.branch.city.timezone
        try:
            current_day = datetime.strptime(request.GET.get('current_day'), '%Y-%m-%d').replace(day=1)
            self.year, self.month = current_day.year, current_day.month
        except TypeError:
            self.year, self.month = datetime.today().year, datetime.today().month

        get_month = request.GET.get('get_month')
        if self.year and self.month and get_month != 'current':
            self.start_month = date(self.year, self.month, 1)
        else:
            self.start_month = date(date.today().year, date.today().month, 1)
        if get_month == 'prev':
            self.start_month -= timedelta(days=1)
            self.start_month = self.start_month.replace(day=1)
        elif get_month == 'next':
            self.start_month += timedelta(days=calendar.monthrange(self.start_month.year, self.start_month.month)[1])
        self.start_month = datetime.combine(self.start_month, datetime.max.time()).replace(day=1)
        self.end_month = datetime(self.start_month.year, self.start_month.month,
                                  calendar.monthrange(self.start_month.year, self.start_month.month)[1], 23, 59
                                  )
        self.year = self.start_month.year
        self.month = self.start_month.month
        self.workers = self.get_workers()
        self.work_shifts = self.get_work_shift()

        self.filters = self.set_filters(request)
        self.filters_q = self.model.get_filters_q(self.request, filters=self.filters)

        return super().dispatch(request, *args, **kwargs)

    def set_filters(self, request):
        filters = dict(
            ordered=['branch'],
            fields=dict(
                branch=dict(
                    label='Филиал', key='branch',
                    widget=dict(attrs={}, name='Select', input_type='select', model_name='company.Branch')
                ),
            )
        )
        filters = self.get_filters(request, filters=filters)
        filters = filters_choices(request, filters, self.model)
        return filters

    def get_work_shift(self):
        timetable_q = TimeTable.objects.filter(
            branch=self.branch,
            plan_start_datetime__gte=self.start_month.date(),
            plan_end_datetime__lt=self.end_month
        )

        if self.filters_q:
            timetable_q = timetable_q.filter(self.filters_q)

        items = dict()
        values = ['id', 'user', 'cache',
                  'plan_start_datetime', 'plan_end_datetime', 'fact_start_datetime', 'fact_end_datetime']
        for item in timetable_q.values(*values):
            item['plan_start_datetime'] += timedelta(hours=self.timezone)
            item['plan_end_datetime'] += timedelta(hours=self.timezone)
            try:
                item['fact_start_datetime'] += timedelta(hours=self.timezone)
                item['fact_end_datetime'] += timedelta(hours=self.timezone)
                item['fact_start_datetime'] = item['fact_start_datetime'].strftime(DATETIME_FORMAT)
                item['fact_end_datetime'] = item['fact_end_datetime'].strftime(DATETIME_FORMAT)
            except TypeError:
                pass
            day = item['plan_start_datetime'].strftime('%Y-%m-%d')
            if day not in items:
                items[day] = dict()
            if item['user'] not in items[day]:
                if item['user'] not in self.workers['users']:
                    _user = User.objects.get(pk=item['user'])
                    self.workers['users'][item['user']] = dict(
                        shifts=0, hours=0,
                        full_name=_user.cache.get('full_name', ''), short_name=_user.cache.get('short_name', '')
                    )
                self.workers['users'][item['user']]['shifts'] += 1
                self.workers['users'][item['user']]['hours'] += item['cache'].get('time_int', 0)
                items[day][item['user']] = dict(
                    id=item['id'],
                    plan_start_datetime=item['plan_start_datetime'].strftime(DATETIME_FORMAT),
                    plan_end_datetime=item['plan_end_datetime'].strftime(DATETIME_FORMAT),
                    fact_start_datetime=item['fact_start_datetime'],
                    fact_end_datetime=item['fact_end_datetime'],
                    time_int=item['cache'].get('time_int', 0),
                    time_str=item['cache'].get('time_str', '')
                )
        return items

    def get_month_set(self):
        days = []
        for day in range(self.start_month.day, self.end_month.day + 1):
            item = date(self.year, self.month, day)
            days.append(dict(
                day=item.day,
                iso=item.strftime('%Y-%m-%d'),
                month=item.month,
                weekday=item.weekday(),
            ))
        return dict(
            year=self.year,
            month=self.month,
            month_name=_(self.start_month.strftime('%B')),
            week_heads=[_(name) for name in calendar.day_abbr],
            days=days
        )

    def get_workers(self):
        users_ordered, users = [], dict()
        for user in self.branch.workers.all().values('id', 'cache'):
            users_ordered.append(user['id'])
            users[user['id']] = dict(
                full_name=user['cache'].get('full_name'),
                short_name=Person.get_short_name(user['cache'].get('full_name')),
                shifts=0,
                hours=0,
            )
        return dict(users_ordered=users_ordered, users=users)

    def get_time_groups(self):
        groups = []
        for group in self.branch.time_groups.filter(
                Q(start_date__gte=self.start_month, start_date__lte=self.end_month) |
                Q(end_date__gte=self.start_month, end_date__lte=self.end_month) |
                Q(start_date__lte=self.start_month, end_date__gte=self.end_month)
        ):
            groups.append(dict(
                id=group.id,
                branch=group.branch_id,
                name=group.name,
                timeout=group.timeout,
                start_date=group.start_date if group.start_date > self.start_month.date() else self.start_month.date(),
                end_date=group.end_date if group.end_date < self.end_month.date() else self.end_month.date(),
                start_time=group.start_time.strftime('%H:%M'),
                end_time=group.end_time.strftime('%H:%M'),
            ))
        return groups

    def get(self, request, *args, **kwargs):
        if not request.GET.get('get'):
            return render(request, 'app_vue.jinja2')

        context = dict(
            title=self.model._meta.verbose_name_plural,
            branch=self.branch.id,
            month_set=self.get_month_set(),
            workers=self.workers,
            work_shifts=self.work_shifts,
            start_time=self.start_time,
            end_time=self.end_time,
            time_groups=self.get_time_groups(),
            filters=self.filters,
            permissions=self.permissions,
            current_day=self.start_month.strftime('%Y-%m-%d')
        )

        if self.request.GET.get('debug'):
            return render_to_response('debug.jinja2', locals())
        return JsonResponse(context, safe=False)


class TimeTableSet(LoginRequiredMixin, View):
    """
        Обработка набора рабочих дней
    """
    model = TimeTable
    branch = None
    timezone = 0
    start_time = None
    end_time = None
    shift_set = dict()
    action = None
    permissions = []

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        self.permissions = self.model.get_permissions(self.request)
        self.action = kwargs.get('action')
        self.action = 'change' if self.action == 'save' else self.action
        if self.action not in self.permissions:
            return HttpResponse('no perm')
        try:
            self.branch = Branch.objects.get(pk=request.GET.get('branch', 65))
        except (ValueError, Branch.DoesNotExist):
            pass
            # self.branch = User.objects.get(pk=request.user.person.id).manager_branches.first().id
        self.timezone = self.branch.city.timezone
        self.start_time = datetime.strptime(request.POST.get('start_time').replace('"', ''), '%H:%M')
        self.end_time = datetime.strptime(request.POST.get('end_time').replace('"', ''), '%H:%M')
        self.shift_set = json.loads(request.POST.get('shift_set', '{}'))

        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        for user_id, shifts in self.shift_set.items():
            user = User.objects.get(pk=user_id)
            if self.action == 'change':
                for shift in shifts:
                    _start_time = datetime.strptime(shift, '%Y-%m-%d') \
                                      .replace(hour=self.start_time.hour, minute=self.start_time.minute) \
                                  - timedelta(hours=self.timezone)
                    _end_time = datetime.strptime(shift, '%Y-%m-%d') \
                                    .replace(hour=self.end_time.hour, minute=self.end_time.minute) \
                                - timedelta(hours=self.timezone)
                    TimeTable.objects.create(branch=self.branch,
                                             user=user,
                                             plan_start_datetime=_start_time,
                                             plan_end_datetime=_end_time
                                             )

            if self.action == 'delete':
                for shift in shifts:
                    _start_time = datetime.strptime(shift, '%Y%m%d').replace(hour=0, minute=0)
                    _end_time = datetime.strptime(shift, '%Y%m%d').replace(hour=23, minute=59)
                    TimeTable.objects.filter(
                        branch=self.branch,
                        user=user,
                        plan_start_datetime__gte=_start_time,
                        plan_end_datetime__lte=_end_time
                    ).delete()

        context = dict(
            title=self.model._meta.verbose_name_plural,
            branch=self.branch.id,
        )
        return JsonResponse(context, safe=False)


class TimeTableShift(FormView):
    model = TimeTable
    user = None
    shift = None
    action = None
    permissions = []

    def dispatch(self, request, *args, **kwargs):
        self.permissions = self.model.get_permissions(self.request)

        self.action = kwargs.get('action')
        self.action = 'change' if self.action == 'save' else self.action
        # if self.action not in self.permissions:
        #     return HttpResponse('no perm')
        try:
            self.shift = self.model.objects.get(pk=kwargs.get('pk'))
        except self.model.DoesNotExist:
            pass
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):
        kwargs = self.get_form_kwargs()
        kwargs.update(dict(
            initial=self.kwargs
        ))
        initial = json.loads(self.request.GET.get('initial', '{}'))
        initial.update(dict(request=self.request))
        try:
            branch = self.shift.branch
        except AttributeError:
            branch = Branch.objects.get(pk=initial.get('branch') or self.request.POST.get('branch'))
        timezone = branch.city.timezone
        if initial.get('plan_start_datetime'):
            initial['plan_start_datetime'] = datetime.strptime(initial['plan_start_datetime'], '%Y-%m-%dT%H:%M') \
                                             - timedelta(hours=timezone)
        if initial.get('plan_end_datetime'):
            initial['plan_end_datetime'] = datetime.strptime(initial['plan_end_datetime'], '%Y-%m-%dT%H:%M') \
                                           - timedelta(hours=timezone)
        kwargs['initial'].update(initial)

        if 'data' in kwargs:
            kwargs['data'] = normalise_data(self.model, kwargs['data'])

        print('kwargs', kwargs)
        form = TimeTableForm(**kwargs)
        if self.shift:
            form = TimeTableForm(instance=self.shift, **kwargs)

        # Смещаем по часовому поясу
        for form_field in ['plan_start_datetime', 'plan_end_datetime', 'fact_start_datetime', 'fact_end_datetime']:
            if form.initial.get(form_field):
                form.initial[form_field] += timedelta(hours=timezone)
        return form

    def post(self, request, *args, **kwargs):
        if self.action not in self.permissions:
            return HttpResponse('no perm')

        if self.action == 'delete':
            self.shift.delete()
            context = dict(
                deleted=True,
                message=dict(type='success', text='Удалено'),
            )
            return JsonResponse(context)

        form = self.get_form()
        if form.is_valid():
            form.save()
            self.shift = form.instance
            context = dict(
                id=self.shift.id,
                message=dict(type='success', text='Сохранено')
            )
            return JsonResponse(context)
        else:
            return JsonResponse(dict(
                form=dict(errors=form.errors)
            ))

    def get(self, request, *args, **kwargs):
        if not request.GET:
            return render(request, 'app_vue.jinja2')
        _form = RemoteForm(self.get_form(), model=self.model, csrf_token=csrf.get_token(self.request)).as_dict()
        context = dict(
            title=self.shift.cache.get('title', None) if self.shift else 'Новая смена',
            form=_form,
            permissions=self.permissions
        )

        if self.request.GET.get('debug'):
            return render_to_response('debug.jinja2', locals())
        return JsonResponse(context)
