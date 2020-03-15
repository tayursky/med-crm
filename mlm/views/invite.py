import json
from django.core import serializers
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, login, get_user_model
from django.urls import reverse, reverse_lazy
from django.http import HttpResponse, JsonResponse
from django.views.generic import DetailView, ListView, TemplateView, View, FormView
from django.shortcuts import render, get_object_or_404, redirect
from django.forms.models import modelform_factory

from mlm.forms import InviteForm
from deal.models import Client, Deal
from identity.models import Account, Person
from mlm.models import Agent, Invite
from sms.models import Sms


class InviteView(FormView):
    model = Agent
    object = None
    token = None
    template_name = 'inside/invite.jinja2'
    form_class = InviteForm
    success_url = reverse_lazy('partner')

    def dispatch(self, request, *args, **kwargs):
        self.token = kwargs.get('token')
        try:
            self.object = self.model.objects.get(token=self.token)
        except Agent.DoesNotExist:
            redirect('identity:login')
            # pass
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):
        form_class = modelform_factory(self.model, form=InviteForm, fields=[])
        if self.request.POST:
            return form_class(self.request.POST, instance=self.object)
        return form_class(instance=self.object)

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            form.save()
            user = get_user_model().objects.get(username=self.object.person.account.username)
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        if self.object:
            context = super().get_context_data(**kwargs)
            context.update(dict(
                title='Приглашение',
                title_h1='Для активации аккаунта, заполните форму',
                object=self.object,
                token=self.token,
            ))
            if 'form' not in context:
                context['form'] = self.get_form()
        else:
            context = dict(
                title='Приглашение',
                title_h1='Неверный токен',
            )
        return context

    def get(self, request, *args, **kwargs):
        if not self.object:
            return redirect('identity:login')
        return super().get(request, *args, **kwargs)


class InviteSend(LoginRequiredMixin, ListView):
    model = Invite
    deal = None
    person = None
    channel = None
    permissions = []
    message = dict()

    def dispatch(self, request, *args, **kwargs):
        self.permissions = self.model.get_permissions(request)
        self.channel = request.GET.get('channel')
        try:
            self.deal = Deal.objects.get(pk=request.GET.get('deal'))
        except Deal.DoesNotExist:
            pass
        try:
            self.person = Person.objects.get(pk=request.GET.get('person'))
        except Person.DoesNotExist:
            pass

        print('deal:', self.deal, 'person:', self.person, 'channel:', self.channel)
        if self.channel == 'sms':
            self.channel_sms()

        return super().dispatch(request, *args, **kwargs)

    def channel_sms(self):
        if self.deal:
            for person in self.deal.persons.all():
                self.sms_person(person)
        elif self.person:
            self.sms_person(self.person)

    def sms_person(self, person):
        phone = person.get_phone()
        if phone:
            mlm_agent = Agent.create_agent(person)
            sms = mlm_agent.send_invite(self.deal)
            self.message = dict(type='success', text='Отправлено')

    def get(self, request, *args, **kwargs):
        context = dict(
            permissions=self.permissions,
            message=self.message,
        )
        if request.GET.get('debug'):
            from django.shortcuts import render_to_response
            return render_to_response('debug.jinja2', locals())

        return JsonResponse(context)
