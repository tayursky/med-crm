import calendar
import decimal
from datetime import date, datetime, timedelta

from django.http import JsonResponse
from django.views.generic import View, ListView
from django.utils.translation import ugettext as _
from django.shortcuts import render, render_to_response

from company.models import Branch
from identity.utils import LoginRequiredMixin
from deal.models import Deal, Service, Stage
from utils.date_time import delta_minutes
from deal.views.deal_calendar import DealCalendar


class MonthView(LoginRequiredMixin, DealCalendar, View):
    """
        Календарь: месяц
    """
    timezone, start, end = 0, None, None
    permissions = []

    def dispatch(self, request, *args, **kwargs):
        self.permissions = Deal.get_permissions(request)
        self.branch = Branch.objects.get(pk=request.GET.get('branch', 65))
        self.timezone = self.branch.city.timezone
        try:
            self.start = datetime.strptime(request.GET.get('current_day'), '%Y-%m-%d').date()
        except (ValueError, TypeError):
            self.start = date.today()
        steps = dict(prev=-1, next=32)
        step = request.GET.get('step', None)
        if not self.start or step == 'current':
            self.start = date.today()
        elif step:
            self.start += timedelta(days=steps.get(step))
        self.start += timedelta(hours=self.timezone)  # timezone
        self.start = self.start.replace(day=1)
        self.end = self.start.replace(day=calendar.monthrange(self.start.year, self.start.month)[1])

        return super().dispatch(request, *args, **kwargs)

    def get_deals(self):
        deal_queryset = Deal.objects.filter(
            branch=self.branch,
            stage__step__gt=0,
            start_datetime__gt=self.start - timedelta(self.start.weekday()),
            start_datetime__lt=self.end + timedelta(days=7 - self.end.weekday())
        )
        deals = dict()
        for deal in deal_queryset.values('start_datetime', 'stage__step'):
            deal['start_datetime'] += timedelta(hours=self.timezone)
            day = deal['start_datetime'].strftime('%Y-%m-%d')
            step = deal['stage__step']
            if day not in deals:
                deals[day] = dict()
            if step not in deals[day]:
                deals[day][step] = 0
            deals[day][step] += 1
        return deals

    def get_month_set(self):
        days = []
        weeks = []
        year = self.start.year
        month = self.start.month

        for weekday in range(self.start.weekday()):
            item = self.start - timedelta(days=(self.start.weekday() - weekday))
            days.append(item)

        for day in range(self.start.day, self.end.day + 1):
            item = date(year, month, day)
            days.append(item)

        for index, weekday in enumerate(range(self.end.weekday(), 6), start=1):
            item = self.end + timedelta(days=index)
            days.append(item)

        week_index = days[0].isocalendar()[1]
        week = []
        for day in days:
            if week_index != int(day.strftime('%V')):
                week_index = int(day.strftime('%V'))
                weeks.append(week)
                week = []
            week.append(dict(
                iso=day.strftime('%Y-%m-%d'),
                label=day.strftime('%d.%m.%Y'),
                month=day.month,
                weekday=day.weekday(),
            ))
        weeks.append(week)

        return dict(
            deals=self.get_deals(),
            today=date.today().strftime('%d.%m.%Y'),
            today_key=date.today().strftime('%Y%m%d'),
            year=year,
            month=month,
            month_name=_(self.start.strftime('%B')),
            week_head=[_(name) for name in calendar.day_abbr],
            weeks=weeks,
        )

    def get(self, request, *args, **kwargs):
        if 'view' not in self.permissions:
            return JsonResponse(dict(answer='No permissions'), safe=False)
        if not request.GET:
            return render(request, 'app_vue.jinja2')
        _, branch_set = self.get_branch_set()
        context = dict(
            current_day=self.start.strftime('%Y-%m-%d'),
            branch_set=branch_set,
            month_set=self.get_month_set(),
            stages=self.stages
        )

        if self.request.GET.get('debug'):
            return render_to_response('debug.jinja2', locals())
        return JsonResponse(context, safe=False)
