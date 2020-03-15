import decimal
import json
from collections import OrderedDict
from datetime import date, datetime, timedelta

from django.db.models import Q
from django.views.generic import ListView
from django.views.generic.edit import View, FormView
from django.shortcuts import render, render_to_response
from django.middleware import csrf
from django.http import HttpResponse, JsonResponse
from django.forms.models import modelform_factory, modelformset_factory, inlineformset_factory

from absolutum.mixins import CoreMixin, DisplayMixin
from company.models import Branch, User
from deal.models import Client, Deal, Stage
from identity.models import Person
from identity.utils import LoginRequiredMixin
from sms.models import Sms
from utils.choices import get_choices, filters_choices
from utils.date_time import get_datetime_string


class DealHistoryListView(LoginRequiredMixin, ListView, CoreMixin):
    """
        История сделки / клиента
    """
    model = None
    client = None
    deal = None
    account_timezone = None
    permissions = []

    def dispatch(self, request, *args, **kwargs):
        self.permissions = Deal.get_permissions(request)
        self.account_timezone = request.user.person.timezone or 0
        try:
            self.client = Client.objects.get(pk=self.request.GET.get('client'))
        except Client.DoesNotExist:
            self.deal = Deal.objects.get(pk=self.request.GET.get('deal'))
        except Deal.DoesNotExist:
            pass
        return super().dispatch(request, *args, **kwargs)

    def get_client_history(self, *args, **kwargs):
        history = dict()
        if not self.client:
            return history

        # comment_values = ['id', 'created_at', 'comment']
        # for comment in self.client.comments.all().values(*comment_values):
        #     history[comment['created_at']] = dict(
        #         time=get_datetime_string(comment['created_at'], self.account_timezone),
        #         label='Комментарий',
        #         name='task_%s' % comment['id'],
        #         new=comment['comment'],
        #     )
        #
        # task_values = ['id', 'time_planned', 'time_completed', 'title', 'comment']
        # for task in self.client.tasks.filter(status='done').values(*task_values):
        #     history[task['time_completed']] = dict(
        #         time=get_datetime_string(task['time_completed'], self.account_timezone),
        #         label='Задача: %s' % task['title'],
        #         name='task_%s' % task['id'],
        #         new=task['comment'],
        #     )

        client = self.client.history.first()
        for client_next in self.client.history.all()[0:]:
            delta = client.diff_against(client_next)
            history_user = None
            if client_next.history_user_id:
                history_user = Person.objects.get(account=client_next.history_user_id).get_short_name_display()
            fields = [i.field for i in delta.changes]
            if 'start_datetime' in fields or 'finish_datetime' in fields:
                old = ''
                if client_next.start_datetime and client_next.finish_datetime:
                    old = '%s (%s)' % (client_next.start_datetime.strftime('%d.%m.%Y %H:%M'),
                                       int((client_next.finish_datetime - client_next.start_datetime).seconds / 60))
                new = ''
                if client.start_datetime:
                    new = '%s (%s)' % (client.start_datetime.strftime('%d.%m.%Y %H:%M'),
                                       int((client.finish_datetime - client.start_datetime).seconds / 60))
                history[client_next.history_date] = dict(
                    time=get_datetime_string(client.history_date, self.account_timezone),
                    label='Время сеанса',
                    name='start_datetime',
                    new=new,
                    old=old,
                    history_user=history_user,
                )
            microseconds = 0
            for change in delta.changes:
                if change.field in ['cache', 'created_at', 'manager', 'start_datetime', 'finish_datetime']:
                    continue

                history[client_next.history_date + timedelta(microseconds=microseconds)] = dict(
                    time=get_datetime_string(client.history_date, self.account_timezone),
                    label=self.client._meta.get_field(change.field).verbose_name,
                    name=change.field,
                    old=change.old,
                    new=change.new,
                    history_user=history_user
                )
                microseconds += 1
            client = client_next

        client = self.client.history.last()
        if client:
            history_user = ''
            if client.history_user_id:
                history_user = Person.objects.get(account=client.history_user_id).get_short_name_display()

            history[client.history_date - timedelta(microseconds=1)] = dict(
                time=get_datetime_string(client.history_date, self.account_timezone),
                label='Клиент создан',
                name='created',
                history_user=history_user
            )

        history_list = []
        for key in sorted(history.keys()):
            history_list.append(history[key])
        history_list.reverse()

        return history_list

    def get_deal_history(self, *args, **kwargs):
        history = dict()
        if not self.deal:
            return history

        comment_values = ['id', 'created_at', 'comment']
        for comment in self.deal.comments.all().values(*comment_values):
            history[comment['created_at']] = dict(
                label='Комментарий',
                name='task_%s' % comment['id'],
                time=get_datetime_string(comment['created_at'], self.account_timezone),
                new=comment['comment']
            )

        task_values = ['id', 'time_planned', 'time_completed', 'title', 'comment']
        for task in self.deal.tasks.filter(status='done').values(*task_values):
            history[task['time_completed']] = dict(
                label='Задача: %s' % task['title'],
                name='task_%s' % task['id'],
                time=get_datetime_string(task['time_completed'], self.account_timezone),
                new=task['comment']
            )

        # sms_values = ['id', 'time_created', 'time_sent', 'phone', 'status', 'status_text', 'text']
        # for sms in self.deal.sms.all().values(*sms_values):
        #     time = sms['time_sent'] or sms['time_created']
        #     status = Sms.SMS_STATUS_NAME[sms['status']].lower()
        #     label = 'СМС %s' % status
        #     if sms['phone']:
        #         label = 'СМС для %s (%s)' % (sms['phone'], Sms.SMS_STATUS_NAME[sms['status']].lower())
        #     history[time] = dict(
        #         label=label,
        #         name='sms_%s' % sms['id'],
        #         status_text=sms['status_text'],
        #         time=get_datetime_string(time, self.account_timezone),
        #         new=sms['text']
        #     )

        timezone = self.deal.branch.city.timezone
        deal = self.deal.history.first()
        for deal_next in self.deal.history.all()[0:]:
            delta = deal.diff_against(deal_next)
            history_user = None
            if deal_next.history_user_id:
                history_user = Person.objects.get(account=deal_next.history_user_id).get_short_name_display()
            fields = [i.field for i in delta.changes]
            if 'start_datetime' in fields or 'finish_datetime' in fields:
                old = ''
                if deal_next.start_datetime and deal_next.finish_datetime:
                    time = deal_next.start_datetime + timedelta(hours=timezone)
                    old = '%s (%s)' % (time.strftime('%d.%m.%Y %H:%M'),
                                       int((deal_next.finish_datetime - deal_next.start_datetime).seconds / 60))
                new = ''
                if deal.start_datetime:
                    time = deal.start_datetime + timedelta(hours=timezone)
                    new = '%s (%s)' % (time.strftime('%d.%m.%Y %H:%M'),
                                       int((deal.finish_datetime - deal.start_datetime).seconds / 60))
                history[deal_next.history_date] = dict(
                    label='Время сеанса',
                    name='start_datetime',
                    time=get_datetime_string(deal.history_date, self.account_timezone),
                    new=new,
                    old=old,
                    history_user=history_user
                )
            microseconds = 0
            for change in delta.changes:
                if change.field in ['cache', 'created_at', 'manager', 'start_datetime', 'finish_datetime']:
                    continue
                elif change.field == 'branch':
                    change.old = Branch.objects.get(pk=change.old).__str__() if change.old else ''
                    change.new = Branch.objects.get(pk=change.new).__str__() if change.new else ''
                elif change.field == 'stage':
                    change.old = Stage.objects.get(pk=change.old).__str__() if change.old else ''
                    change.new = Stage.objects.get(pk=change.new).__str__() if change.new else ''
                elif change.field == 'master':
                    change.old = User.objects.get(pk=change.old).__str__() if change.old else ''
                    change.new = User.objects.get(pk=change.new).__str__() if change.new else ''
                elif change.field == 'status':
                    change.old = Deal.DEAL_STATUS_NAME.get(change.old)
                    change.new = Deal.DEAL_STATUS_NAME.get(change.new)

                history[deal_next.history_date + timedelta(microseconds=microseconds)] = dict(
                    label=self.deal._meta.get_field(change.field).verbose_name,
                    name=change.field,
                    time=get_datetime_string(deal.history_date, self.account_timezone),
                    old=change.old,
                    new=change.new,
                    history_user=history_user
                )
                microseconds += 1
            deal = deal_next

        self.deal.history.last()
        history_user = ''
        if deal.history_user_id:
            history_user = Person.objects.get(account=deal.history_user_id).get_short_name_display()
        history[deal.history_date - timedelta(microseconds=1)] = dict(
            label='Сделка создана',
            name='created',
            time=get_datetime_string(deal.history_date, self.account_timezone),
            history_user=history_user
        )

        history_list = []
        for key in sorted(history.keys()):
            history_list.append(history[key])
        history_list.reverse()

        return history_list

    def get(self, request, *args, **kwargs):
        if 'view' not in self.permissions:
            return JsonResponse(dict(answer='No permissions'), safe=False)
        if not request.GET:
            return render(request, 'app_vue.jinja2')

        context = dict(
            title='История',
            history=self.get_client_history() or self.get_deal_history(),
        )
        return JsonResponse(context, safe=False)
