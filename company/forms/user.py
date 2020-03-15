from collections import OrderedDict
from django import forms
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _

from directory.forms import DirectoryForm
from identity.models import Account, Person
from company.models import User


class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['username', 'email', 'is_active']


class UserForm(DirectoryForm):
    account_form = None

    class Meta:
        model = User
        fields = User.list_form_fields

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance = kwargs.get('instance', self.instance)

        # print('kwargs', kwargs)

        account_kwargs = dict(data=kwargs.get('data', {}))
        if self.instance.account:
            account_kwargs.update(dict(instance=self.instance.account))
        self.account_form = AccountForm(**account_kwargs)

        self.fields['username'] = self.account_form.fields['username']
        self.fields['password'] = forms.CharField(required=True, label=_('Password'), max_length=128)
        self.fields['password'].widget.input_type = 'password'
        self.fields['is_active'] = self.account_form.fields['is_active']

        if self.instance:
            for field_name in self.instance._meta.model.list_form_fields:
                self.fields[field_name].initial = getattr(self.instance, field_name)

            self.fields['username'].initial = self.account_form.initial.get('username', '')
            self.fields['is_active'].initial = self.account_form.initial.get('is_active', True)
            if self.account_form.initial:
                self.fields['password'].required = False

    def clean_username(self):
        data = self.cleaned_data.get('username')
        query_set = Account.objects.filter(username=data).exclude(pk=self.account_form.instance.id)
        if query_set.exists():
            raise forms.ValidationError(_(u'Такой логин уже используется'))
        return data

    def clean_password(self):
        data = self.cleaned_data.get('password')
        # if not self.account_form.initial:
        #     raise forms.ValidationError(_(u'Необходим пароль'))
        return data

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.account_form.is_valid():
            self.account_form.save()
            self.instance.account = self.account_form.instance
            if self.cleaned_data.get('password'):
                self.account_form.instance.set_password(self.cleaned_data.get('password'))
                self.account_form.instance.save()
            self.instance.save()
            self.instance.account.is_staff = True
            self.instance.account.save()
        else:
            print('ERRORS', self.account_form.errors)
