from collections import OrderedDict
from django import forms
from django.db.models import Q
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _

from directory.forms import DirectoryForm
from identity.models import Account, Person
from company.models import TimeGroup, User


class TimeGroupForm(DirectoryForm):
    account_form = None

    class Meta:
        model = TimeGroup
        fields = TimeGroup.list_form_fields

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance = kwargs.get('instance', self.instance)

        if not self.initial.get('request').user.has_perm('Администраторы'):
            self.fields['branch'].widget.choices.queryset = self.fields['branch'].choices.queryset.filter(
                managers=self.initial.get('request').user.person.id
            )

    def clean(self):
        branch, users = self.cleaned_data.get('branch'), self.cleaned_data.get('users')
        start_date, end_date = self.cleaned_data.get('start_date'), self.cleaned_data.get('end_date')
        start_time, end_time = self.cleaned_data.get('start_time'), self.cleaned_data.get('end_time')
        print(start_date, end_date)
        for user in users:
            time_group = self.model.objects.filter(
                Q(branch=branch, users=user) &
                Q(
                    Q(start_date__lte=start_date, end_date__gte=start_date) |
                    Q(start_date__lte=end_date, end_date__gte=end_date) |
                    Q(start_date__gte=start_date, end_date__lte=end_date)
                ) &
                Q(
                    Q(start_time__lte=start_time, end_time__gt=start_time) |
                    Q(start_time__lt=end_time, end_time__gte=end_time)
                )
            ).exclude(pk=self.instance.id)
            if time_group.exists():
                raise forms.ValidationError(
                    {'end_time': _(u'В этом интервале уже есть группа (%s)' % time_group.first())}
                )

        return super().clean()
