import decimal
import json
from datetime import datetime, date, timedelta

from django.db.models import Q, Count, Subquery
from django.http import JsonResponse
from django.views.generic import ListView
from django.views.generic.edit import FormView, View
from django.shortcuts import render, render_to_response
from django.middleware import csrf
from django.http import HttpResponse, JsonResponse
from django.forms.models import modelform_factory, modelformset_factory, inlineformset_factory
from django.utils.translation import ugettext as _

from company.models import TimeTable, TimeGroup
from deal.models import Client, Deal, ServiceTimetable
# from deal.forms import DealForm, DealPersonForm, DealTaskForm
from identity.forms import PersonFindForm
from identity.models import Person
from sms.models import *
from utils.remote_forms.forms import RemoteForm
from utils.date_time import get_month_name


def sms_check_deal(deal, resend=None):
    # TODO deal.branch.city_id и branch__city_id заменить на branch.periodic
    # sms.deal_datetime - учитывается при сохранении сделки,
    # если deal.step > 2 и нет записи с deal_datetime - создается sms
    now = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    start_date = now + timedelta(days=1)
    finish_date = start_date + timedelta(days=1)
    if resend:
        sms_sent = False
    else:
        if not deal.start_datetime or deal.start_datetime <= datetime.now():
            print('\nescape sms_check_deal\n')
            return None
        if deal.branch.periodic and deal.stage.step < 4:
            return None

        sms_sent = deal.sms.filter(deal_datetime=deal.start_datetime).exists()

    print('SMS deal.stage.step', deal.stage.step)
    # TODO: дифференцировать рассылку для регионов, сейчас Москва рассылка при подтвердении / регионы предоплаты
    if (deal.branch.city_id == 1 and deal.stage.step > 2 and not sms_sent) or \
            (deal.branch.city_id != 1 and deal.stage.step > 3 and not sms_sent):
        template_list = ['deal_confirmed_center', 'deal_confirmed_region',
                         'deal_remind_1day_center', 'deal_remind_1day_region']
        template_name = 'deal_confirmed_region' if deal.branch.periodic else 'deal_confirmed_center'
        template_q = SmsTemplate.objects.get(name=template_name)
        template = template_q.template

        deal.sms.filter(status='wait', template__name__in=template_list).update(status='cancel')
        timezone = deal.branch.city.timezone
        for person in deal.persons.filter(rel_deals__primary=True):
            _start_datetime = deal.start_datetime + timedelta(hours=timezone)
            start_datetime = deal.start_datetime + timedelta(hours=timezone)
            timetable = TimeGroup.objects.filter(
                branch=deal.branch, users=deal.master,
                start_date__lte=_start_datetime.date(), end_date__gte=_start_datetime.date(),
                start_time__lte=_start_datetime.time(), end_time__gt=_start_datetime.time(),
            ).exclude(timeout=True).first()
            if timetable:
                start_datetime = start_datetime.replace(hour=timetable.start_time.hour,
                                                        minute=timetable.start_time.minute)
            datetime_string = '%s %s (%s) %s' % (
                int(start_datetime.strftime('%d')),
                get_month_name(start_datetime.strftime('%m')),
                _(start_datetime.strftime('%a')).upper(),
                start_datetime.strftime('%H:%M')
            )
            text = template.format(
                start_datetime=datetime_string,
                address=deal.branch.address,
                branch_phone=deal.branch.phone or ''
            )
            # Если сделка только на контроль, то убираем 'Оплата наличными.'
            if not deal.rel_persons.filter(control=False).exists():
                text = text.replace('Оплата наличными.', '')

            Sms.objects.create(
                deal=deal,
                deal_datetime=deal.start_datetime,
                person=person,
                text=text,
                template=template_q
            )


def deal_remind_1day():
    now = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    start_date = now + timedelta(days=1)
    finish_date = now + timedelta(days=2)
    print('\nperiod:', start_date, finish_date)

    template_list = ['deal_remind_1day_center', 'deal_remind_1day_region']
    deal_qs = Deal.objects.filter(
        Q(status='in_work',
          start_datetime__gte=start_date,
          start_datetime__lte=finish_date) &
        Q(
            Q(stage__step__in=[3, 5], branch__city_id=1) |
            Q(stage__step__in=[3, 4], branch__city_id__gt=1)
        )
    ).exclude(sms__template__name__in=template_list)

    # deal.branch.city_id != 1
    for deal in deal_qs:
        template_name = 'deal_remind_1day_region' if deal.branch.periodic else 'deal_remind_1day_center'
        template_q = SmsTemplate.objects.get(name=template_name)
        try:
            timezone = deal.branch.city.timezone
        except:
            timezone = 0

        time_send = now.replace(hour=10)
        print(deal.cache['title'], datetime.now() + timedelta(hours=timezone), time_send)
        if datetime.now() + timedelta(hours=timezone) > time_send:
            print('send now')

            for person in deal.persons.filter(rel_deals__primary=True):
                _start_datetime = deal.start_datetime + timedelta(hours=timezone)
                start_datetime = deal.start_datetime + timedelta(hours=timezone)
                timetable = TimeGroup.objects.filter(
                    branch=deal.branch, users=deal.master,
                    start_date__lte=_start_datetime.date(), end_date__gte=_start_datetime.date(),
                    start_time__lte=_start_datetime.time(), end_time__gt=_start_datetime.time(),
                ).first()
                if timetable:
                    start_datetime = start_datetime.replace(hour=timetable.start_time.hour,
                                                            minute=timetable.start_time.minute)
                datetime_string = '%s %s (%s) %s' % (
                    int(start_datetime.strftime('%d')),
                    get_month_name(start_datetime.strftime('%m')),
                    _(start_datetime.strftime('%a')).upper(),
                    start_datetime.strftime('%H:%M')
                )
                text = template_q.template.format(
                    start_datetime=datetime_string,
                    address=deal.branch.address,
                    branch_phone=deal.branch.phone or ''
                )
                # Если сделка только на контроль, то убираем 'Оплата наличными.'
                if not deal.rel_persons.filter(control=False).exists():
                    text = text.replace('Оплата наличными.', '')

                Sms.objects.get_or_create(
                    deal=deal,
                    deal_datetime=deal.start_datetime,
                    person=person,
                    text=text,
                    template=template_q
                )


def deal_online_created(deal):
    _now = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    template_q = SmsTemplate.objects.get(name='deal_online_created')
    template = template_q.template

    text = template.format(
        deal='%s %s' % (deal.id, deal.branch.city.short),
        person='%s (%s) %s' % (deal.persons.first().get_full_name_display(),
                               deal.persons.first().get_age(),
                               deal.persons.first().get_phone())
    )

    user = deal.branch.managers.first()
    phone = None
    try:
        phone = deal.branch.phone.replace('+', '')
    except AttributeError:
        pass
    if phone:
        Sms.objects.create(
            deal=deal,
            person=user,
            phone=phone,
            text=text,
            template=template_q
        )


class SmsResendView(View):
    client = None
    deal = None

    def dispatch(self, request, *args, **kwargs):
        try:
            self.client = Client.objects.get(pk=self.request.GET.get('client'))
        except Client.DoesNotExist:
            self.deal = Deal.objects.get(pk=self.request.GET.get('deal'))
        except Deal.DoesNotExist:
            pass
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if self.deal:
            sms_check_deal(self.deal, True)
            print('sms_check_deal')
        context = dict(answer='done')

        return JsonResponse(context, safe=False)
