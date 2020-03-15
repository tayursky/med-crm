import json

from datetime import datetime, date
from django.urls import reverse, reverse_lazy
from django.forms import ModelForm, \
    Form, ModelChoiceField, ModelMultipleChoiceField, \
    Textarea, ValidationError, FileField, BooleanField, DecimalField, MultipleChoiceField
from django.forms.widgets import Select, Input, HiddenInput, TextInput


class DirectoryForm(ModelForm):
    model = None
    widgets = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = self.Meta.model
        self.widgets = getattr(self.model, 'widgets', {})
        parent_name = getattr(self.model, 'parent_name', None)

        if parent_name:
            self.widgets.update({parent_name: ParentWidget})

        for field_name, widget in self.widgets.items():
            widget = widget(**kwargs)
            self.fields[field_name].widget = widget
            if hasattr(widget, 'value'):
                self.fields[field_name].initial = widget.value

        # Attrs
        for field_name, attrs in getattr(self.model, 'list_attrs', {}).items():
            if field_name in self.fields:
                for attr, value in attrs.items():
                    related_field = getattr(self.model, field_name)
                    try:
                        related_model = related_field.field.related_model
                    except AttributeError:
                        related_model = None
                    if attr == 'remote_search' and related_model:
                        self.fields[field_name].queryset = related_model.objects.none()
                        pk_list = []
                        if self.initial.get(field_name):
                            pk_list.append(self.initial.get(field_name))
                        if self.data.get(field_name):
                            pk_list.append(self.data.get(field_name))
                        if pk_list:
                            _pk_list = []
                            for pk in pk_list:
                                try:
                                    _pk_list.append(int(pk))
                                except ValueError:
                                    pass
                            self.fields[field_name].queryset = related_model.objects.filter(pk__in=_pk_list)

                        if hasattr(self.model, 'list_select_related'):
                            self.fields[field_name].queryset = self.fields[field_name].queryset \
                                .select_related(getattr(self.model, 'list_select_related'))

                    elif attr == 'relations' and related_model:
                        relations = dict()
                        for rel_key, rel_name in value.items():
                            relations[rel_key] = dict()
                            print('rel_name', rel_name, related_model)
                            related_name = getattr(related_model, rel_name).field.related_query_name()
                            for obj in getattr(related_model, rel_name).field.related_model.objects.all():
                                relations[rel_key][obj.id] = \
                                    [i['id'] for i in getattr(obj, related_name).all().values('id')]
                        value = relations

                    elif attr == 'required':
                        self.fields[field_name].required = value

                    self.fields[field_name].widget.attrs.update({attr: value})


class ParentWidget(Select):
    model = None
    parent_object = None
    value = None

    def __init__(self, attrs=None, choices=(), *args, **kwargs):
        super().__init__(attrs)
        initial = kwargs.get('initial', {})
        self.model = initial.get('model', None)
        self.parent_object = initial.get('parent_object', None)
        if self.parent_object:
            self.value = self.parent_object.id
            self.attrs.update({'disabled': True})


class FilterForm(DirectoryForm):
    model = None
    list_filters = []
    widgets = None

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = self.Meta.model
        self.list_filters = getattr(self.model, 'list_filters', [])
        self.widgets = getattr(self.model, 'widgets', {})

        for filter_name in self.list_filters:

            default = None  # Значение по умолчанию
            if isinstance(filter_name, tuple):
                filter_name, default = filter_name
            init = request.GET.get(filter_name, default)

            if init and ',' in init:
                init = init.split(',')

            # TODO: сделать отсев по атрибуту "input_type='daterange'" в моделе, сейчас отсев по "[]"
            _key = '%s[]' % filter_name
            if _key in request.GET.keys():
                json_str = str(request.GET).replace('<QueryDict: ', '').replace('>', '')
                init = eval(json_str)[_key]

            self.fields[filter_name].initial = init
