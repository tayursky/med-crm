from django.contrib.auth.forms import AuthenticationForm
from django import forms


class PersonFindForm(forms.Form):
    person = forms.ChoiceField(
        label=u'Найти персону',
        widget=forms.Select(
            attrs=dict(remote_search='directory/remote_search/person/')
            # attrs=dict(remote_search=reverse('dir:remote_search', kwargs={'model_name': 'client_user'}))
        )
    )
