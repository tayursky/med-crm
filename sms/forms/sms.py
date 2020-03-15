from datetime import date, datetime, timedelta

from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse, reverse_lazy
from django import forms
from phonenumber_field.formfields import PhoneNumberField

from directory.forms import DirectoryForm
from identity.models import PersonPhone
from deal.models import Deal, DealPerson, Service, DealTask
from utils.normalize_data import normalise_phone


class SmsForm(DirectoryForm):
    class Meta:
        model = DealTask
        fields = DealTask.list_form_fields

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        initial = kwargs.get('initial', {})
        self.fields['deal'].widget.choices.queryset = Deal.objects.none()
        try:
            self.deal = Deal.objects.get(pk=initial.get('deal'))
            self.fields['deal'].widget.choices.queryset = Deal.objects.filter(pk=initial.get('deal'))
        except Deal.DoesNotExist:
            self.deal = None

        self.fields['deal'].widget.attrs.update({'hidden': True})
        self.fields['status'].widget.attrs.update({'hidden': True})

        # print('DealForm, args:', args)
        print('DealTaskForm, kwargs:', kwargs)

    # def clean_time_planned(self):
    #     data = self.cleaned_data.get('time_planned')
    #     if not data:
    #         print('no time')
    #         pass
    #     return data

    def clean(self):
        # if self.cleaned_data.get('interval') and self.cleaned_data.get('start_datetime'):
        #     self.cleaned_data['finish_datetime'] = self.cleaned_data.get('start_datetime') + \
        #                                            timedelta(minutes=self.cleaned_data.get('interval'))
        return super().clean()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # if 'status' in self.changed_data and self.data.get('status') == 'ok':
        #     self.instance.time_completed = datetime.now()
        #     self.instance.save()
        # import ipdb; ipdb.set_trace()
