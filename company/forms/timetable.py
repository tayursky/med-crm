from collections import OrderedDict
from django import forms
from django.db.models import Q
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _

from directory.forms import DirectoryForm
from identity.models import Account, Person
from company.models import TimeTable, User


class TimeTableForm(DirectoryForm):
    account_form = None

    class Meta:
        model = TimeTable
        fields = TimeTable.list_form_fields

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance = kwargs.get('instance', self.instance)

        if not self.initial.get('request').user.has_perm('Администраторы'):
            self.fields['branch'].widget.choices.queryset = self.fields['branch'].choices.queryset.filter(
                managers=self.initial.get('request').user.person.id
            )

    def clean(self):
        return super().clean()
