from django.contrib.auth.forms import AuthenticationForm
from django import forms
from django.core.mail import send_mail

from directory.forms import DirectoryForm
from identity.models import Account, Person


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Пользователь',
        label_suffix='',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Номер телефона'}))
    password = forms.CharField(
        label='Пароль',
        label_suffix='',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}))


class AccountRecoveryFormStep1(DirectoryForm):
    email = forms.EmailField(label='E-mail')

    class Meta:
        model = Account
        fields = ['email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean_email(self):
        data = self.cleaned_data['email']
        if not Account.objects.filter(person__emails__value=self.data.get('email')).first():
            raise forms.ValidationError('Пользователя с таким email нет')
        return data

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.instance:
            person = self.instance.person
            person.token = Account.objects.make_random_password(length=12)
            person.save()
            send_mail('Правка: восстановление пароля',
                      'Ссылка на восстановление пароля: '
                      'https://crm.pravkaatlanta.ru/identity/recover/?token=%s' % person.token,
                      'admin@pravkaatlanta.ru',
                      [self.data.get('email')],
                      fail_silently=False
                      )


class AccountRecoveryFormPass(DirectoryForm):
    new_password = forms.CharField(
        label='Новый пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    new_password2 = forms.CharField(
        label='Повторите пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Account
        fields = ['new_password', 'new_password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean_new_password2(self):
        if 0 < len(self.cleaned_data['new_password']) < 5:
            raise forms.ValidationError('Пароль не меньше 5 символов')
        if self.cleaned_data['new_password'] != self.cleaned_data['new_password2']:
            raise forms.ValidationError('Пароли должны совпадать')
        return self.cleaned_data['new_password']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.instance.set_password(self.cleaned_data['new_password'])
        self.instance.save()
        person = self.instance.person
        person.token = None
        person.save()
