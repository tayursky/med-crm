import json
from datetime import date, datetime, timedelta

from django.views.generic import View
from django.urls import reverse_lazy
from django.http import HttpResponse, JsonResponse
from django.core.mail import send_mail

from deal.forms.online import OnlineShortForm, OnlinePartnerForm
from utils.remote_forms.forms import RemoteForm
from sms.views.sms import deal_online_created
from mlm.models import Agent


class OnlineSpiderView(View):
    """
        Онлайн запись
    """
    answer = None

    def dispatch(self, request, *args, **kwargs):
        self.kwargs['promocode'] = request.GET.get('promo')
        return super().dispatch(request, *args, **kwargs)

    def get_form(self):
        form_class = OnlineShortForm
        kwargs = dict(
            initial=self.kwargs,
        )
        if self.request.GET.get('last_name') or self.request.GET.get('last_name') == '':
            kwargs.update(dict(
                data=self.request.GET
            ))
            form = form_class(**kwargs)
            print('post')
            if form.is_valid():
                deal_online_created(form.save())
                print('valid')
                self.answer = 'done'
                return None
            else:
                self.answer = 'error'
        return form_class(**kwargs)

    def get(self, request, *args, **kwargs):
        form = self.get_form()
        context = dict(
            title='Онлайн-заявка',
            form=RemoteForm(form).as_dict() if form else None,
            answer=self.answer
        )
        return JsonResponse(context)


class OnlineSpiderPartnerView(View):
    """
        Онлайн регистрация партнера
    """
    answer = None

    def dispatch(self, request, *args, **kwargs):
        self.kwargs['promocode'] = request.GET.get('promo')
        return super().dispatch(request, *args, **kwargs)

    def get_form(self):
        form_class = OnlinePartnerForm
        kwargs = dict(
            initial=self.kwargs,
        )
        if self.request.GET.get('last_name') or self.request.GET.get('last_name') == '':
            kwargs.update(dict(
                data=self.request.GET
            ))
            form = form_class(**kwargs)
            if form.is_valid():
                person = form.save()
                mlm_agent = Agent.create_pretender(person)
                send_mail('Новый претендент',
                          'Персона: %s' % person,
                          'admin@pravkaatlanta.ru',
                          ['tayursky@gmail.com'],
                          fail_silently=False
                          )
                self.answer = 'В ближайшее время, мы вам перезвоним.'

        return form_class(**kwargs)

    def get(self, request, *args, **kwargs):
        form = self.get_form()
        context = dict(
            title='Регистрация в партнерской программе',
            form=RemoteForm(form).as_dict() if form else None,
            answer=self.answer
        )
        return JsonResponse(context)
