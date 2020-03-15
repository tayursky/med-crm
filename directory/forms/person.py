from django.urls import reverse, reverse_lazy
from django.forms import ModelForm, \
    Form, ModelChoiceField, ModelMultipleChoiceField, \
    Textarea, ValidationError, FileField, BooleanField, DecimalField, MultipleChoiceField
from django.forms.widgets import Select, Input, HiddenInput, TextInput

from directory.forms import DirectoryForm
from deal.models import ServiceTimetable
from identity.models import Person


class PersonForm(DirectoryForm):
    class Meta:
        model = Person
        fields = Person.list_form_fields

    def __init__(self, attrs=None, choices=(), *args, **kwargs):
        super().__init__(attrs)
        initial = kwargs.get('initial', {})
        if self.parent_object:
            self.value = self.parent_object.id
            self.attrs.update({'disabled': True})


class ServiceTimetableForm(DirectoryForm):
    class Meta:
        model = ServiceTimetable
        fields = ServiceTimetable.list_form_fields

    def __init__(self, attrs=None, choices=(), *args, **kwargs):
        super().__init__(attrs)
        initial = kwargs.get('initial', {})
        if self.parent_object:
            self.value = self.parent_object.id
            self.attrs.update({'disabled': True})
