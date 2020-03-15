from decimal import Decimal
from datetime import date, datetime, time, timedelta

from django.core.exceptions import ObjectDoesNotExist
from django import forms

from company.models import EventLog
from company.models import Branch
from directory.forms import DirectoryForm
from identity.models import PersonPhone, PersonEmail
from deal.models import Deal, DealPerson, Service
from identity.models import Person, PersonContact


class DealForm(DirectoryForm):
    interval = forms.IntegerField(
        required=False, label_suffix='', label='Продолжительность сеанса', help_text='В минутах',
    )
    request = None
    branch = None
    old_mlm_agent = None

    class Meta:
        model = Deal
        fields = Deal.list_form_fields

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial.update(kwargs.get('initial', {}))
        # print('INITIAL', self.initial)
        self.fields['interval'].initial = self.initial.get('interval')
        try:
            self.branch = Branch.objects.get(pk=self.initial.get('branch'))
            timezone = self.branch.city.timezone
        except Branch.DoesNotExist:
            self.branch = None
            timezone = self.instance.branch.city.timezone

        self.request = self.initial.get('request')
        self.old_mlm_agent = self.instance.mlm_agent if self.instance else None
        self.fields['start_datetime'].label = 'Время сеанса'

        if 'instance' in kwargs:
            if not self.fields['interval'].initial:
                if self.instance.start_datetime and self.instance.finish_datetime:
                    interval = (self.instance.finish_datetime - self.instance.start_datetime).seconds / 60
                else:
                    interval = self.branch.interval
                    interval = interval.hour * 60 + interval.minute
                self.fields['interval'].initial = interval

            if self.instance.start_datetime:
                self.fields['start_datetime'].initial = self.instance.start_datetime + timedelta(hours=timezone)
                self.initial['start_datetime'] = self.fields['start_datetime'].initial
            if self.instance.finish_datetime:
                self.fields['finish_datetime'].initial = self.instance.finish_datetime + timedelta(hours=timezone)
                self.initial['finish_datetime'] = self.fields['finish_datetime'].initial

        elif 'data' not in kwargs:
            self.fields['stage'].initial = self.fields['stage'].queryset.get(name='new').id
            self.fields['master'].initial = Deal.get_master(self.branch)

        if self.initial.get('start_iso'):
            self.fields['start_datetime'].initial = \
                datetime.strptime(self.initial.get('start_iso'), '%Y-%m-%dT%H:%M')
            self.initial['start_datetime'] = self.fields['start_datetime'].initial

            if self.initial.get('end_iso'):
                self.fields['finish_datetime'].initial = \
                    datetime.strptime(self.initial.get('end_iso'), '%Y-%m-%dT%H:%M')
                self.fields['interval'].initial = (self.fields['finish_datetime'].initial -
                                                   self.fields['start_datetime'].initial).seconds / 60

        if not self.fields['interval'].initial and self.initial.get('interval'):
            self.fields['interval'].initial = int(self.initial.get('interval'))
        elif not self.fields['interval'].initial:
            self.fields['interval'].initial = self.branch.interval.hour * 60 + self.branch.interval.minute

        null_list = ['0.00', Decimal(0.0)]
        self.fields['cost'].initial = '' if self.fields['cost'].initial in null_list else self.fields['cost'].initial
        self.fields['paid'].initial = '' if self.fields['paid'].initial in null_list else self.fields['paid'].initial
        self.fields['paid_non_cash'].initial = '' if self.fields['paid_non_cash'].initial in null_list \
            else self.fields['paid_non_cash'].initial

    def clean_finish_datetime(self):
        data = None
        if self.initial.get('interval') and self.cleaned_data.get('start_datetime'):
            data = self.cleaned_data.get('start_datetime') + timedelta(minutes=int(self.initial.get('interval')))
        elif self.cleaned_data.get('finish_datetime'):
            data = self.cleaned_data.get('finish_datetime')
        return data

    def clean_mlm_agent(self):
        data = self.cleaned_data.get('mlm_agent')
        if self.old_mlm_agent and self.old_mlm_agent != self.cleaned_data.get('mlm_agent'):
            EventLog.objects.create(
                account=self.request.user,
                event_type='deal_change_mlm_agent',
                event='Сделка {deal_id}, новый агент: {to_mlm_agent}, старый агент: {from_mlm_agent}'.format(
                    deal_id=self.instance.id,
                    to_mlm_agent=self.cleaned_data.get('mlm_agent'),
                    from_mlm_agent=self.old_mlm_agent),
            )
            if not self.request.user.has_perm('Администраторы'):
                raise forms.ValidationError('Вы не можете менять промокод')
        return data

    def clean(self):
        discount = self.cleaned_data.get('discount')
        comment = self.cleaned_data.get('comment')
        if discount and not comment:
            raise forms.ValidationError({'comment': 'При наличии скидки обязателен комментарий'})

        return super().clean()

    def save(self, *args, **kwargs):
        return super().save()


class DealPersonForm(DirectoryForm):
    primary = forms.BooleanField(required=False, initial=False, label_suffix='', label='О.')
    control = forms.BooleanField(required=False, initial=False, label_suffix='', help_text='Контроль', label='К.')
    full_name = forms.CharField(required=True, label_suffix='', label='Фамилия Имя Отчество')
    phone = forms.CharField(max_length=32, required=False, label_suffix='', label='Телефон')
    birthday = forms.DateField(required=False, label_suffix='', help_text='День рождения', label='День рожд.')

    deal = None
    prefix = 0
    person = None
    last_name = None
    first_name = None
    patronymic = None

    class Meta:
        model = DealPerson
        fields = ['primary', 'control', 'full_name', 'birthday', 'phone']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.empty_permitted = False
        self.fields['primary'].widget.attrs.update({'el_col': 2})
        self.fields['control'].widget.attrs.update({'el_col': 2})
        self.fields['full_name'].widget.attrs.update({'el_col': 9, 'placeholder': 'Фамилия Имя Отчество'})
        self.fields['birthday'].widget.attrs.update({'el_col': 4, 'placeholder': 'День рождения'})
        self.fields['phone'].widget.attrs.update({'el_col': 7, 'mask': '\+1 (111) 111-11111', 'placeholder': 'Телефон'})

        if 'instance' in kwargs and self.instance.person:
            self.fields['full_name'].initial = self.instance.person.get_full_name_display()

        try:
            self.deal = self.data['%s-deal' % kwargs['prefix']]
        except KeyError:
            self.deal = Deal.objects.none()

        self.prefix = kwargs.get('prefix', 0)

    def clean_full_name(self):
        data = self.cleaned_data['full_name'].strip().split(' ')
        print(data)
        if len(data) < 2:
            raise forms.ValidationError('Фамилия и имя обязательны')
        self.last_name = data[0]
        self.first_name = data[1]
        self.patronymic = ' '.join(data[2:]).strip() if len(data) > 2 else ''
        return data

    def clean_phone(self):
        data = self.cleaned_data.get('phone')
        if self.cleaned_data.get('primary') and not data:
            raise forms.ValidationError('Обязательное поле')
        return data

    def clean(self):
        # person = Person.objects.filter(last_name=self.last_name,
        #                                first_name=self.first_name,
        #                                patronymic=self.patronymic,
        #                                birthday=self.cleaned_data.get('birthday')).first()
        # if person:
        #     raise forms.ValidationError('Человек с таким Ф.И.О. и днем рождения уже есть')
        return super().clean()

    def has_changed(self):

        return bool(self.changed_data)
        # return any(form.has_changed() for form in self)
        # changed = False
        # import ipdb; ipdb.set_trace()
        # for form in self:
        #     if form.has_changed():
        #         changed = True
        # return changed

    def save(self, *args, **kwargs):
        try:
            self.person = Person.objects.get(pk=self.data['%s-person_id' % self.prefix])
        except (KeyError, Person.DoesNotExist):
            self.person = Person.objects.create()
        self.person.last_name = self.last_name
        self.person.first_name = self.first_name
        self.person.patronymic = self.patronymic
        self.person.birthday = self.cleaned_data['birthday']
        self.person.save()

        phone = self.person.phones.first()
        if phone:
            phone.value = self.cleaned_data.get('phone')
            phone.save()
        else:
            phone_queryset = PersonPhone.objects.create(person=self.person, value=self.cleaned_data.get('phone'))
            self.person.phones.add(phone_queryset)

        self.person.save()

        self.instance.deal = self.deal
        self.instance.person = self.person
        self.instance.save()
        return self.instance
