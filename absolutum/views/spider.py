import json
from datetime import date, datetime, timedelta

from django.views.generic import TemplateView, FormView
from django.urls import reverse_lazy

from deal.forms.online import OnlineShortForm
from sms.views.sms import deal_online_created


class SpiderView(TemplateView):
    template_name = 'inside/spider.jinja2'

    # def dispatch(self, request, *args, **kwargs):
    #     from directory.models import WorkingDaysCalendar
    #     WorkingDaysCalendar.calendar_parse(year=2019)
    #     return super().dispatch(request, *args, **kwargs)

    # def get(self, request, *args, **kwargs):
    #     context = dict()
    #     from django.shortcuts import render_to_response
    #     return render_to_response('debug.jinja2', locals())


class SpiderPartnerView(TemplateView):
    template_name = 'inside/spider_partner.jinja2'
