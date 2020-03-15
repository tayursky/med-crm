from decimal import Decimal

from datetime import date, datetime, timedelta

from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse, reverse_lazy
from django import forms

from company.models import Branch, Master
from deal.models import Deal, DealPerson, Stage, Service
from directory.forms import DirectoryForm
from identity.models import PersonPhone, PersonEmail
from identity.models import Person
from mlm.models import Agent
from utils.normalize_data import normalise_phone
from utils.clean_data import get_numbers

MASTERS = [i['id'] for i in Master.objects.filter(account__is_active=True).values('id')]
BRANCHES = Branch.objects.filter(is_active=True).values('id', 'name', 'city__name').distinct()
# MASTERS = [i['id'] for i in Master.objects.all().values('id')]
# BRANCHES = [dict(id=1, city__name=1)]
BRANCHES_CHOICES = [(i['id'], i['city__name']) for i in BRANCHES]


class DateInput(forms.DateInput):
    input_type = 'date'


class OnlineShortForm(forms.ModelForm):
    branch = forms.ChoiceField(choices=BRANCHES_CHOICES,
                               required=True, label_suffix='', widget=forms.Select(), label='Город')
    last_name = forms.CharField(max_length=32, required=True, label_suffix='', label='Фамилия')
    first_name = forms.CharField(max_length=32, required=True, label_suffix='', label='Имя')
    patronymic = forms.CharField(max_length=32, required=False, label_suffix='', label='Отчество')
    phone = forms.CharField(max_length=32, required=True, label_suffix='', label='Телефон')
    email = forms.EmailField(required=False, label_suffix='', label='E-mail')
    birthday = forms.DateField(widget=DateInput, label_suffix='', label='День рождения')
    comment = forms.CharField(max_length=32, required=False, label_suffix='', label='Комментарий')

    promocode = forms.CharField(max_length=32, required=False, label_suffix='', label='Промокод')
    discount = forms.CharField(max_length=32, required=False, label_suffix='', label='Скидка',
                               widget=forms.HiddenInput())
    mlm_agent = None

    class Meta:
        model = Person
        fields = ['branch', 'last_name', 'first_name', 'patronymic', 'birthday', 'phone']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        initial_promocode = kwargs.get('initial', {}).get('promocode')
        if initial_promocode:
            self.fields['promocode'].initial = initial_promocode.upper()
            try:
                self.mlm_agent = Agent.objects.get(code=self.fields['promocode'].initial)
                self.fields['discount'].initial = int(self.mlm_agent.discount)
                self.fields['promocode'].widget = forms.HiddenInput()
            except Agent.DoesNotExist:
                pass

    def clean(self):
        return super().clean()

    def clean_phone(self):
        data = get_numbers(self.cleaned_data.get('phone'))
        if len(data) != 11:
            raise forms.ValidationError('Номер телефона 11 цифр')
        return data

    def clean_promocode(self):
        data = self.cleaned_data.get('promocode')
        try:
            self.mlm_agent = Agent.objects.get(code=data.upper())
        except Agent.DoesNotExist:
            pass
        return data

    def save(self, *args, **kwargs):
        branch = Branch.objects.get(pk=self.cleaned_data.get('branch'))
        person = Person.objects.create(
            last_name=self.cleaned_data.get('last_name'),
            first_name=self.cleaned_data.get('first_name'),
            patronymic=self.cleaned_data.get('patronymic'),
            birthday=self.cleaned_data.get('birthday')
        )
        person.phones.create(value=self.cleaned_data.get('phone'))
        if self.cleaned_data.get('email'):
            person.emails.create(value=self.cleaned_data.get('email'))
        # TODO: прописать стоимость правки
        cost = Decimal('15000.00')
        if self.mlm_agent:
            cost -= cost / 100 * self.mlm_agent.discount
        deal = Deal.objects.create(
            branch=branch,
            stage=Stage.objects.get(name='new'),
            comment='Онлайн заявка. %s' % self.cleaned_data.get('comment'),
            mlm_agent=self.mlm_agent,
            cost=cost,
        )
        deal.services.add(Service.objects.get(name='Правка'))
        deal.persons.add(person)
        return deal  # super().save(commit=False)


class OnlinePartnerForm(forms.ModelForm):
    last_name = forms.CharField(max_length=32, required=True, label_suffix='', label='Фамилия')
    first_name = forms.CharField(max_length=32, required=True, label_suffix='', label='Имя')
    patronymic = forms.CharField(max_length=32, required=False, label_suffix='', label='Отчество')
    phone = forms.CharField(max_length=32, required=True, label_suffix='', label='Телефон')
    email = forms.EmailField(label_suffix='', label='E-mail')
    birthday = forms.DateField(widget=DateInput, label_suffix='', label='День рождения')
    social_link = forms.CharField(max_length=128, required=False, label_suffix='', label='Страница вконтакте')
    comment = forms.CharField(max_length=32, required=True, label_suffix='', label='Комментарий')

    class Meta:
        model = Person
        fields = ['last_name', 'first_name', 'patronymic', 'phone', 'email', 'birthday', 'social_link', 'comment']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['comment'].widget.attrs.update(dict(placeholder='Где и когда прошли Правку'))

    def clean(self):
        return super().clean()

    def clean_phone(self):
        data = get_numbers(self.cleaned_data.get('phone'))
        if len(data) != 11:
            raise forms.ValidationError('Номер телефона 11 цифр')
        if Person.objects.filter(phones__value=data).exists():
            raise forms.ValidationError('Этот телефон уже используется')
        return data

    def clean_email(self):
        data = self.cleaned_data.get('email')
        if Person.objects.filter(emails__value=data).exists():
            raise forms.ValidationError('Этот email уже используется')
        return data

    def save(self, *args, **kwargs):
        person = Person.objects.create(
            last_name=self.cleaned_data.get('last_name'),
            first_name=self.cleaned_data.get('first_name'),
            patronymic=self.cleaned_data.get('patronymic'),
            birthday=self.cleaned_data.get('birthday'),
            comment=self.cleaned_data.get('comment')
        )
        person.contacts.create(value=self.cleaned_data.get('social_link'), type=1)
        person.phones.create(value=self.cleaned_data.get('phone'))
        if self.cleaned_data.get('email'):
            person.emails.create(value=self.cleaned_data.get('email'))
        return person


class OnlineDealForm(DirectoryForm):
    interval = forms.IntegerField(
        required=False, label_suffix='', label='Продолжительность сеанса', help_text='В минутах',
    )
    service = None

    class Meta:
        model = Deal
        fields = ['start_datetime', 'finish_datetime', 'comment']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        initial = kwargs.get('initial', {})
        try:
            self.service = Service.objects.get(pk=initial.get('service'))
        except KeyError:
            self.service = Service.objects.get(pk=self.data['service'])
        # timezone = self.service.branch.city.timezone

        # print('DealForm, args:', args)
        # print('DealForm, kwargs:', kwargs)

        # self.fields['service_type'].widget.choices.queryset = self.service.template.service_types.all()

        # if self.service:
        # primary_service_type = self.service.template.service_types.filter(primary=True) \
        #     .values('id', 'cost').first()

        # self.fields['service_type'].initial = primary_service_type['id']

    def clean(self):
        if self.cleaned_data.get('start_datetime') and self.cleaned_data.get('interval'):
            self.cleaned_data['finish_datetime'] = self.cleaned_data.get('start_datetime') + \
                                                   timedelta(minutes=self.cleaned_data.get('interval'))
        return super().clean()

    def save(self, *args, **kwargs):
        self.instance.step = self.service.template.steps.first()
        return super().save()


class OnlineDealPersonForm(DirectoryForm):
    primary = forms.BooleanField(required=False, initial=False, label_suffix='', label='Основной')
    control = forms.BooleanField(required=False, initial=False, label_suffix='', label='Контроль',
                                 help_text='Контрольная диагностика после правки')
    last_name = forms.CharField(required=True, label_suffix='', label='Фамилия')
    first_name = forms.CharField(required=True, label_suffix='', label='Имя')
    patronymic = forms.CharField(required=False, label_suffix='', label='Отчество')
    birthday = forms.DateField(required=False, label='День рождения')
    phone = forms.CharField(max_length=32, required=False, label_suffix='', label='Телефон')
    email = forms.EmailField(required=False, label_suffix='', label='E-mail')

    deal = None
    person = None
    prefix = 0

    class Meta:
        model = DealPerson
        fields = ['primary', 'control', 'last_name', 'first_name', 'patronymic', 'birthday', 'phone', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        initial = kwargs.get('initial', {})

        self.fields['primary'].widget.attrs.update({'el_col': 3, 'hidden': True})
        self.fields['control'].widget.attrs.update({'el_col': 3})
        self.fields['first_name'].widget.attrs.update({'el_col': 10})
        self.fields['phone'].widget.attrs.update({'el_col': 8, 'mask': '\+1 (111) 111-1111'})

        try:
            self.deal = self.data['%s-deal' % kwargs['prefix']]
        except KeyError:
            self.deal = Deal.objects.none()

        self.prefix = kwargs.get('prefix', 0)

    def clean_phone(self):
        data = self.cleaned_data.get('phone')
        # print(self.cleaned_data.get('primary'))
        if self.cleaned_data.get('primary') and not data:
            raise forms.ValidationError('Для основного контакта, обязательное поле')
        return data

    def clean(self):
        return super().clean()

    def has_changed(self):
        return bool(self.changed_data)

    def save(self, *args, **kwargs):
        # print(self.changed_data)
        try:
            self.person = Person.objects.get(pk=self.data['%s-person_id' % self.prefix])
        except (KeyError, Person.DoesNotExist):
            # import ipdb; ipdb.set_trace()
            self.person = Person.objects.create()
            # pass
        self.person.last_name = self.cleaned_data['last_name']
        self.person.first_name = self.cleaned_data['first_name']
        self.person.patronymic = self.cleaned_data['patronymic']
        self.person.birthday = self.cleaned_data['birthday']
        self.person.save()

        phone = self.person.phones.first()
        if phone:
            phone.value = self.cleaned_data.get('phone')
            phone.save()
        else:
            phone_queryset = PersonPhone.objects.create(person=self.person, value=self.cleaned_data.get('phone'))
            self.person.phones.add(phone_queryset)
        email = self.person.emails.first()
        if email:
            email.value = self.cleaned_data.get('email')
            email.save()
        else:
            phone_queryset = PersonEmail.objects.create(person=self.person, value=self.cleaned_data.get('email'))
            self.person.emails.add(phone_queryset)
        self.person.save()

        self.instance.deal = self.deal
        self.deal.cost = self.deal.service.template.service_types.filter(primary=True).first().cost
        self.deal.save()

        self.instance.person = self.person
        self.instance.save()

        return self.instance
