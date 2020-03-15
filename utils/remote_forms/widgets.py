import datetime
from collections import OrderedDict
from django.utils.dates import MONTHS
from directory.forms import ParentWidget


class RemoteWidget(object):
    def __init__(self, widget, model=None, field_name=None):
        self.model = model
        self.field_name = field_name
        self.widget = widget

    def as_dict(self):
        widget_dict = OrderedDict()
        # import ipdb; ipdb.set_trace()
        # print('widget.__class__', self.widget.__class__.__name__)
        widget_dict['name'] = self.widget.__class__.__name__
        widget_dict['is_hidden'] = self.widget.is_hidden
        widget_dict['needs_multipart_form'] = self.widget.needs_multipart_form
        widget_dict['is_localized'] = self.widget.is_localized
        widget_dict['is_required'] = self.widget.is_required
        widget_dict['attrs'] = self.widget.attrs

        if hasattr(self.widget, 'input_type'):
            widget_dict['input_type'] = self.widget.input_type

        return widget_dict


class RemoteInput(RemoteWidget):
    def as_dict(self):
        widget_dict = super(RemoteInput, self).as_dict()
        return widget_dict


class RemoteTextInput(RemoteInput):
    def as_dict(self):
        return super(RemoteTextInput, self).as_dict()


class RemotePasswordInput(RemoteInput):
    def as_dict(self):
        return super(RemotePasswordInput, self).as_dict()


class RemoteHiddenInput(RemoteInput):
    def as_dict(self):
        return super(RemoteHiddenInput, self).as_dict()


class RemoteEmailInput(RemoteInput):
    def as_dict(self):
        widget_dict = super(RemoteEmailInput, self).as_dict()
        widget_dict['name'] = 'TextInput'
        widget_dict['input_type'] = 'text'
        return widget_dict


class RemoteNumberInput(RemoteInput):
    def as_dict(self):
        widget_dict = super(RemoteNumberInput, self).as_dict()
        widget_dict['name'] = 'TextInput'
        return widget_dict


class RemoteURLInput(RemoteInput):
    def as_dict(self):
        widget_dict = super(RemoteURLInput, self).as_dict()
        widget_dict['name'] = 'TextInput'
        return widget_dict


class RemoteMultipleHiddenInput(RemoteHiddenInput):
    def as_dict(self):
        widget_dict = super(RemoteMultipleHiddenInput, self).as_dict()
        widget_dict['choices'] = self.widget.choices
        return widget_dict


class RemoteFileInput(RemoteInput):
    def as_dict(self):
        return super(RemoteFileInput, self).as_dict()


class RemoteClearableFileInput(RemoteFileInput):
    def as_dict(self):
        widget_dict = super(RemoteClearableFileInput, self).as_dict()
        widget_dict['initial_text'] = self.widget.initial_text
        widget_dict['input_text'] = self.widget.input_text
        widget_dict['clear_checkbox_label'] = self.widget.clear_checkbox_label
        return widget_dict


class RemoteTextarea(RemoteWidget):
    def as_dict(self):
        widget_dict = super().as_dict()
        widget_dict['input_type'] = 'textarea'
        return widget_dict


class RemoteTimeInput(RemoteInput):
    def as_dict(self):
        widget_dict = super(RemoteTimeInput, self).as_dict()
        widget_dict['format'] = self.widget.format
        widget_dict['input_type'] = 'time'
        return widget_dict


class RemoteDateInput(RemoteTimeInput):
    def as_dict(self):
        widget_dict = super(RemoteDateInput, self).as_dict()
        widget_dict['input_type'] = 'date'

        # current_year = datetime.datetime.now().year
        # widget_dict['choices'] = [{
        #     'title': 'day',
        #     'data': [{'key': x, 'value': x} for x in range(1, 32)]
        # }, {
        #     'title': 'month',
        #     'data': [{'key': x, 'value': y} for (x, y) in MONTHS.items()]
        # }, {
        #     'title': 'year',
        #     'data': [{'key': x, 'value': x} for x in range(current_year - 100, current_year + 1)]
        # }]

        return widget_dict


class RemoteDateTimeInput(RemoteTimeInput):
    def as_dict(self):
        widget_dict = super(RemoteDateTimeInput, self).as_dict()
        widget_dict['input_type'] = 'datetime'

        return widget_dict


class RemoteCheckboxInput(RemoteWidget):
    def as_dict(self):
        widget_dict = super(RemoteCheckboxInput, self).as_dict()
        check_test = None
        if self.widget.check_test is not None:
            check_test = True
        widget_dict['check_test'] = check_test
        widget_dict['input_type'] = 'checkbox'
        return widget_dict


class RemoteSelect(RemoteWidget):
    def as_dict(self):
        optgroup_key = None
        widget_dict = super(RemoteSelect, self).as_dict()
        widget_dict.update({
            'input_type': 'select',
            'choices': []
        })
        if self.model:
            optgroups = getattr(self.model, 'optgroups', [])
            if self.field_name in optgroups:
                optgroup_key = optgroups[self.field_name]
                widget_dict['optgroups'] = []

        if hasattr(self.widget.choices, 'queryset'):
            queryset = self.widget.choices.queryset
            try:
                model = type(self.widget.choices.queryset[0])._meta.model
                if hasattr(model, 'list_select_related'):
                    queryset = queryset.select_related(*getattr(model, 'list_select_related'))
            except IndexError:
                pass
            for query in queryset:
                item = dict(
                    value=query.pk,
                    label=query.__str__(),
                )
                if 'optgroups' in widget_dict:
                    optgroup = getattr(query, optgroup_key, None).__str__()
                    item['optgroup'] = optgroup
                    widget_dict['optgroups'].append(optgroup)

                widget_dict['choices'].append(item)
        else:
            for key, value in self.widget.choices:
                widget_dict['choices'].append(dict(
                    value=key,
                    label=value,
                ))

        if 'optgroups' in widget_dict:
            widget_dict['optgroups'] = sorted(list(set(widget_dict['optgroups'])))

        return widget_dict


class RemoteNullBooleanSelect(RemoteSelect):
    def as_dict(self):
        return super(RemoteNullBooleanSelect, self).as_dict()


class RemoteSelectMultiple(RemoteSelect):
    def as_dict(self):
        widget_dict = super(RemoteSelectMultiple, self).as_dict()
        widget_dict['input_type'] = 'selectmultiple'
        widget_dict['size'] = len(widget_dict['choices'])

        return widget_dict


class RemoteRadioInput(RemoteWidget):
    def as_dict(self):
        widget_dict = OrderedDict()
        widget_dict['title'] = self.widget.__class__.__name__
        widget_dict['name'] = self.widget.name
        widget_dict['value'] = self.widget.value
        widget_dict['attrs'] = self.widget.attrs
        widget_dict['choice_value'] = self.widget.choice_value
        widget_dict['choice_label'] = self.widget.choice_label
        widget_dict['index'] = self.widget.index
        widget_dict['input_type'] = 'radio'

        return widget_dict


class RemoteRadioFieldRenderer(RemoteWidget):
    def as_dict(self):
        widget_dict = OrderedDict()
        widget_dict['title'] = self.widget.__class__.__name__
        widget_dict['name'] = self.widget.name
        widget_dict['value'] = self.widget.value
        widget_dict['attrs'] = self.widget.attrs
        widget_dict['choices'] = self.widget.choices
        widget_dict['input_type'] = 'radio'

        return widget_dict


class RemoteRadioSelect(RemoteSelect):
    def as_dict(self):
        widget_dict = super(RemoteRadioSelect, self).as_dict()

        widget_dict['choices'] = []
        for key, value in self.widget.choices:
            widget_dict['choices'].append({
                'name': self.field_name or '',
                'value': key,
                'label': value
            })

        widget_dict['input_type'] = 'radio'

        return widget_dict


class RemoteCheckboxSelectMultiple(RemoteSelectMultiple):
    def as_dict(self):
        return super(RemoteCheckboxSelectMultiple, self).as_dict()


class RemoteMultiWidget(RemoteWidget):
    def as_dict(self):
        widget_dict = super(RemoteMultiWidget, self).as_dict()

        widget_list = []
        for widget in self.widget.widgets:
            # Fetch remote widget and convert to dict
            widget_list.append()

        widget_dict['widgets'] = widget_list

        return widget_dict


class RemoteSplitDateTimeWidget(RemoteMultiWidget):
    def as_dict(self):
        widget_dict = super(RemoteSplitDateTimeWidget, self).as_dict()
        widget_dict['date_format'] = self.widget.date_format
        widget_dict['time_format'] = self.widget.time_format

        return widget_dict


class RemoteSplitHiddenDateTimeWidget(RemoteSplitDateTimeWidget):
    def as_dict(self):
        return super(RemoteSplitHiddenDateTimeWidget, self).as_dict()


class RemoteParentWidget(RemoteSelect):
    def as_dict(self):
        widget_dict = super().as_dict()
        widget_dict['choices'] = []
        for key, value in self.widget.choices:
            widget_dict['choices'].append({
                'value': key,
                'label': value
            })
        widget_dict['input_type'] = 'select'

        return widget_dict
