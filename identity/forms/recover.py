from django.contrib.auth.forms import AuthenticationForm
from django import forms


class RecoverPasswordForm(forms.Form):
    phone = forms.CharField(label='Номер телефона')

    def clean_phone(self):
        data = self.cleaned_data['phone']
        return data

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
