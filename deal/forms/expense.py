from decimal import Decimal

from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse, reverse_lazy
from django import forms

from deal.models import Expense
from directory.forms import DirectoryForm
from utils.choices import get_choices


class ExpenseForm(DirectoryForm):
    class Meta:
        model = Expense
        fields = Expense.list_form_fields

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # import ipdb; ipdb.set_trace()
        # self.fields['branch'].widget.choices.queryset = get_choices(kwargs['request'], 'company.Master')

    def clean_value(self):
        data = self.cleaned_data.get('value')
        if data <= Decimal(0.0):
            raise forms.ValidationError('Расход должен быть больше нуля')
        return data


DealExpenseForm = ExpenseForm
