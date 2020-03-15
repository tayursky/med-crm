from decimal import Decimal

from django.core import serializers
from django.contrib.auth import authenticate, login, get_user_model
from django.db.models import Avg, Sum
from django.urls import reverse, reverse_lazy
from django.http import HttpResponse, JsonResponse
from django.views.generic import DetailView, ListView, TemplateView, View, FormView
from django.shortcuts import render, render_to_response, get_object_or_404, redirect
from django.forms.models import modelform_factory
from django.contrib.auth.mixins import LoginRequiredMixin
from django.middleware import csrf
from django.core.mail import send_mail

from deal.forms.online import OnlinePartnerForm
from identity.models import Person, PersonPhone, PersonEmail, PersonContact
from company.models import EventLog
from mlm.forms import AgentCabinetForm, AgentPasswordForm
from mlm.models import Agent, Invite
from sms.models import Sms
from utils.normalize_data import normalise_phone


class AgentRegistrationView(FormView):
    template_name = 'inside/mlm_registration.jinja2'
    form_class = OnlinePartnerForm
    answer = None

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):
        if self.request.POST:
            return self.form_class(self.request.POST)
        return self.form_class()

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        phone = normalise_phone(form.data.get('phone'))
        person_phone = Person.objects.filter(phones__value=phone)
        person_no_phone = Person.objects.filter(
            cache__full_name='%s %s %s' % (
                form.data.get('last_name'),
                form.data.get('first_name'),
                form.data.get('patronymic')
            ),
            birthday=form.data.get('birthday'))
        if person_phone.exists():
            person = person_phone.first()
            person.birthday = form.data.get('birthday')
            person.save()
            PersonEmail.objects.create(person=person, value=form.data.get('email'))
            if form.data.get('social_link'):
                PersonContact.objects.create(person=person, type=1, value=form.data.get('social_link'))
            mlm_agent = Agent.create_agent(person)
            text_template = 'Приглашаем в партнерскую программу: {url}'
            text = text_template.format(
                url='http://crm.pravkaatlanta.ru/partner/invite/%s/' % mlm_agent.token,
            )
            Sms.objects.create(
                person=person, phone=phone, text=text, cache=dict(mlm='invite')
            )
            self.answer = 'На ваш номер телефона выслан инвайт.'
            return render(request, self.template_name, self.get_context_data())
        elif person_no_phone.exists():
            person = person_no_phone.first()
            PersonPhone.objects.create(person=person, value=phone)
            PersonEmail.objects.create(person=person, value=form.data.get('email'))
            if form.data.get('social_link'):
                PersonContact.objects.create(person=person, type=1, value=form.data.get('social_link'))
            mlm_agent = Agent.create_agent(person)
            text_template = 'Приглашаем в партнерскую программу: {url}'
            text = text_template.format(
                url='http://crm.pravkaatlanta.ru/partner/invite/%s/' % mlm_agent.token,
            )
            Sms.objects.create(
                person=person, phone=phone, text=text, cache=dict(mlm='invite')
            )
            self.answer = 'На ваш номер телефона выслан инвайт.'
            return render(request, self.template_name, self.get_context_data())
        elif form.is_valid():
            person = form.save()
            mlm_agent = Agent.create_pretender(person)
            send_mail('Новый претендент',
                      'Персона: %s' % person,
                      'admin@pravkaatlanta.ru',
                      ['tayursky@gmail.com'],
                      fail_silently=False
                      )
            self.answer = 'В ближайшее время, мы вам перезвоним.'
            return render(request, self.template_name, self.get_context_data())
        else:
            EventLog.objects.create(
                event_type='mlm_agent_fail_registration', event=form.data.get('phone'), cache=form.data
            )
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = dict(
            title='Регистрация в партнерской программе',
            csrf_token=csrf.get_token(self.request),
            form=self.get_form(),
            answer=self.answer,
        )
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return render(request, self.template_name, context)


class AgentOfferView(LoginRequiredMixin, View):
    agent = None
    template_name = 'inside/mlm_offer.jinja2'

    def dispatch(self, request, *args, **kwargs):
        self.agent = request.user.person.mlm_agent
        if self.request.GET.get('accept') == 'on':
            self.agent.offer_accepted = True
            self.agent.save()
            return redirect('partner')

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = dict(
            title='Договор оферты',
            agent=self.agent,
        )
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return render(request, self.template_name, context)


class AgentHelpView(LoginRequiredMixin, TemplateView):
    template_name = 'inside/mlm_help.jinja2'


class AgentCabinetView(LoginRequiredMixin, View):
    model = Agent
    agent = None
    permissions = []
    template_name = 'inside/mlm_account.jinja2'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('identity:login')

        # if not self.agent:
        #     return redirect('identity:login')

        if self.request.POST.get('code'):
            self.request.POST._mutable = True
            self.request.POST['code'] = self.request.POST.get('code').upper()
        self.permissions = self.model.get_permissions(request)
        self.agent = request.user.person.mlm_agent

        if not self.agent.offer_accepted:
            return redirect('partner_offer')

        return super().dispatch(request, *args, **kwargs)

    def get_invite_set(self):
        total_set = dict(
            count=0,
            sum=Decimal('0.00')
        )
        invite_set = total_set.copy()
        invite_set.update(dict(
            level_1=total_set.copy(),
            level_2=total_set.copy(),
            level_3=total_set.copy(),
            payments=self.agent.payments.all().aggregate(Sum('cost'))['cost__sum'] or Decimal('0.00')
        ))
        for invite in self.agent.invites.filter(agent=self.agent, status='ok'):
            invite_set['level_%s' % invite.level]['count'] += 1
            invite_set['level_%s' % invite.level]['sum'] += invite.cost
            invite_set['count'] += 1
            invite_set['sum'] += invite.cost
        return invite_set

    def get_form(self):
        form_class = AgentCabinetForm
        kwargs = dict(
            initial=dict(),
            label_suffix='',
        )
        if self.request.method in ('POST', 'PUT'):
            kwargs.update(dict(
                data=self.request.POST,
                files=self.request.FILES,
            ))
        return form_class(instance=self.agent, **kwargs)

    def get_form_password(self):
        form_class = AgentPasswordForm
        kwargs = dict(
            initial=dict(),
            label_suffix='',
        )
        if self.request.method in ('POST', 'PUT'):
            kwargs.update(dict(
                data=self.request.POST,
                files=self.request.FILES,
            ))
        return form_class(instance=self.agent, **kwargs)

    def get_context_data(self, **kwargs):
        print(self.agent.code)
        context = dict(
            title='Личный кабинет',
            agent=self.agent,
            invite_set=self.get_invite_set(),
            permissions=self.permissions,
        )
        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        if self.request.POST.get('code'):
            form = self.get_form()
        else:
            form = self.get_form_password()

        if form.is_valid():
            form.save()
            if self.request.POST.get('new_password'):
                user = self.agent.person.account
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                login(request, user)
        else:
            if self.request.POST.get('code'):
                context.update(dict(
                    form=form
                ))
            else:
                context.update(dict(
                    form_password=form
                ))

        return render(request, self.template_name, context)

    def get(self, request, *args, **kwargs):
        # if not self.agent:
        #     return redirect('identity:login')
        context = self.get_context_data()
        if request.GET.get('edit'):
            context.update(dict(
                form=self.get_form()
            ))
        elif request.GET.get('password'):
            context.update(dict(
                form_password=self.get_form_password()
            ))
        return render(request, self.template_name, context)
