from decimal import Decimal
from django.core import serializers
from django.db.models import Avg, Sum
from django.urls import reverse, reverse_lazy
from django.http import HttpResponse, JsonResponse
from django.views.generic import DetailView, ListView, TemplateView, View
from django.shortcuts import render, render_to_response, get_object_or_404, redirect, reverse
from django.forms.models import modelform_factory
from django.contrib.auth.views import LoginView

from django.contrib.auth.mixins import LoginRequiredMixin

from mlm.forms import AgentCabinetForm
from identity.forms import AccountRecoveryFormStep1, AccountRecoveryFormPass
from identity.models import Account, Person
from utils.normalize_data import normalise_phone


class IdentityLoginView(LoginView):

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        self.request.POST._mutable = True
        if self.request.POST.get('username'):
            if self.request.POST.get('username')[0] in ['+', '7', '8'] and \
                    len(self.request.POST.get('username')) > 10:
                self.request.POST['username'] = normalise_phone(self.request.POST.get('username'))
        return kwargs


class IdentityRecoverView(View):
    model = Account
    account = None
    template_name = 'login_recover.jinja2'
    email = None
    token = None
    password = None
    message = None

    def dispatch(self, request, *args, **kwargs):
        self.email = request.POST.get('email')
        self.token = request.GET.get('token')
        self.password = request.POST.get('new_password')
        if self.email:
            self.account = Account.objects.filter(person__emails__value=self.email).first()
        if self.token:
            self.account = Account.objects.filter(person__token=self.token).first()

        return super().dispatch(request, *args, **kwargs)

    def get_form(self):
        form_class = AccountRecoveryFormPass if self.token else AccountRecoveryFormStep1
        # print('form_class', form_class)
        kwargs = dict(
            label_suffix='',
        )
        if self.request.method in ('POST', 'PUT'):
            kwargs.update(dict(data=self.request.POST))
        if self.account:
            kwargs.update(dict(instance=self.account))
        return form_class(**kwargs)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        if self.account:
            if context['form'].is_valid():
                context['form'].save()
                if self.email:
                    context.update(form=None, message='На ваш e-mail отправлен код подтверждения.')
                elif self.token:
                    context.update(form=None,
                                   message='Пароль изменен.',
                                   path_login=reverse('identity:login')
                                   )
        return render(request, self.template_name, context)

    def get_context_data(self, **kwargs):
        context = dict(
            title='Восстановление пароля',
            form=self.get_form(),
            path='{url}?{params}'.format(
                url=self.request.path,
                params='&'.join(['%s=%s' % (k, v) for k, v in self.request.GET.items()])
            )
        )
        if self.token and not self.account:
            context.update(dict(
                message='Неверный токен',
                form=None
            ))

        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return render(request, self.template_name, context)
