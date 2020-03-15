from django import forms
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _

from directory.forms import DirectoryForm
from identity.models import Account, Person
from mlm.models import Agent


class AgentForm(DirectoryForm):
    class Meta:
        model = Agent
        fields = Agent.list_form_fields

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance = kwargs.get('instance', self.instance)
        self.fields.pop('person')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class AgentCabinetForm(DirectoryForm):
    email = forms.EmailField(label='E-mail')
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'new-password'})
    )

    class Meta:
        model = Agent
        fields = ['code', 'email', 'bank_account', 'bank_account_fio', 'password']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password'].widget.attrs.update(dict(placeholder='Ваш текущий пароль'))
        self.fields['bank_account'].widget.attrs.update(dict(placeholder='Номер банковской карты'))
        self.fields['bank_account_fio'].widget.attrs.update(dict(
            placeholder='Имя на карте',
            autocomplete='new-password'))
        self.fields['email'].initial = self.instance.person.get_email()

    def clean_code(self):
        data = self.cleaned_data.get('code')
        if check_code(self.instance, data):
            raise forms.ValidationError('Этот промокод уже используется')
        return data

    def clean_email(self):
        data = self.cleaned_data.get('email')
        if Person.objects.filter(emails__value=data).exclude(pk=self.instance.person.id).exists():
            raise forms.ValidationError('Этот email уже используется')
        return data

    def clean_password(self):
        data = self.cleaned_data.get('password')
        if not self.instance.person.account.check_password(data):
            raise forms.ValidationError('Неверный пароль')
        return data

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        try:
            email = self.instance.person.emails.first()
            email.value = self.cleaned_data['email']
            email.save()
        except AttributeError:
            self.instance.person.emails.create(
                value=self.cleaned_data['email']
            )


class AgentPasswordForm(DirectoryForm):
    new_password = forms.CharField(
        label='Новый пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    new_password2 = forms.CharField(
        label='Повторите пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password = forms.CharField(
        label='Старый пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Agent
        fields = ['new_password', 'new_password2', 'password']

    def clean_new_password2(self):
        if self.cleaned_data['new_password'] == self.instance.person.get_phone():
            raise forms.ValidationError('Пароль не должен совпадать с номером телефона')
        if len(self.cleaned_data['new_password']) < 5:
            raise forms.ValidationError('Пароль не меньше 5 символов')
        if self.cleaned_data['new_password'] != self.cleaned_data['new_password2']:
            raise forms.ValidationError('Пароли должны совпадать')
        return self.cleaned_data['new_password']

    def clean_password(self):
        data = self.cleaned_data.get('password')
        if not self.instance.person.account.check_password(data):
            raise forms.ValidationError('Неверный пароль')
        return data

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.instance.person.account.set_password(self.cleaned_data['new_password'])
        self.instance.person.account.save()


class ManagerCreateAgentForm(DirectoryForm):
    parent = None
    code = forms.CharField(required=False, label='Промокод')
    birthday = forms.DateField(label='День рождения')
    phone = forms.CharField(label='Телефон')
    email = forms.EmailField(label='E-mail')
    comment = forms.CharField(required=False, label='Комментарий')

    class Meta:
        model = Person
        fields = ['first_name', 'patronymic', 'last_name', 'birthday']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent = self.data.get('manager')
        self.fields['birthday'].required = False

    def clean_code(self):
        data = self.cleaned_data.get('code')
        if check_code(self, data):
            raise forms.ValidationError('Этот промокод уже используется')
        return data

    def clean_phone(self):
        data = self.cleaned_data.get('phone')
        if Person.objects.filter(phones__value=data).exists():
            raise forms.ValidationError('Этот номер телефона уже используется')
        return data

    def clean_email(self):
        data = self.cleaned_data.get('email')
        print('email', data)
        if Person.objects.filter(emails__value=data).exists():
            raise forms.ValidationError('Этот email уже используется')
        return data

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.instance.phones.create(value=self.cleaned_data['phone'])
        self.instance.emails.create(value=self.cleaned_data['email'])
        account = Account.objects.create(username=self.cleaned_data['phone'], email=self.cleaned_data['email'])
        self.instance.account = account
        self.instance.save()

        agent = Agent.create_agent(self.instance)
        agent.parent = self.parent
        if self.cleaned_data['code']:
            agent.code = self.cleaned_data['code']
        if self.cleaned_data['comment']:
            agent.comment = self.cleaned_data['comment']
        agent.save()
        agent.send_invite()


def check_code(obj, code):
    code = code.upper()
    if Agent.objects.filter(code=code).exclude(pk=obj.id).exists():
        return True
    words_in = ['ATLANT', 'ATLAS', 'BURLAKOVSKI', 'KARIMOV', 'BONUS', 'NEW', 'PRAVKA']
    words = ['RINAT',
             'PRAVITEL',
             'PRAVSHIK',
             'SVOBODA',
             'ZDOROVIE',
             'YEAR',
             '2021',
             'SALE',
             'AKCIYA',
             'PRAZDNIK']
    if code in words or code in words_in:
        return True
    for word in words_in:
        if code.find(word) > -1:
            return True
    return False
