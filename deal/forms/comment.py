from datetime import date, datetime, timedelta

from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse, reverse_lazy
from django import forms
from phonenumber_field.formfields import PhoneNumberField

from directory.forms import DirectoryForm
from identity.models import PersonPhone
from deal.models import *
from utils.normalize_data import normalise_phone


class DealCommentForm(DirectoryForm):
    class Meta:
        model = DealComment
        fields = DealComment.list_parents + DealComment.list_form_fields

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        initial = kwargs.get('initial', {})
        self.fields['client'].widget.choices.queryset = Client.objects.none()
        self.fields['deal'].widget.choices.queryset = Deal.objects.none()
        # print('DealCommentForm, kwargs:', kwargs)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
