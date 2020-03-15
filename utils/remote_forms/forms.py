from collections import OrderedDict
from utils.remote_forms import fields, logger
from utils.remote_forms.utils import resolve_promise


class RemoteForm(object):
    def __init__(self, form, *args, **kwargs):
        self.form = form

        self.all_fields = set(self.form.fields.keys())

        self.csrf_token = kwargs.get('csrf_token')
        self.excluded_fields = set(kwargs.pop('exclude', []))
        self.included_fields = set(kwargs.pop('include', []))
        self.readonly_fields = set(kwargs.pop('readonly', []))
        self.ordered_fields = kwargs.pop('ordering', [])

        self.fieldsets = kwargs.pop('fieldsets', {})

        # Make sure all passed field lists are valid
        if self.excluded_fields and not (self.all_fields >= self.excluded_fields):
            logger.warning(
                'Excluded fields %s are not present in form fields' % (self.excluded_fields - self.all_fields))
            self.excluded_fields = set()

        if self.included_fields and not (self.all_fields >= self.included_fields):
            logger.warning(
                'Included fields %s are not present in form fields' % (self.included_fields - self.all_fields))
            self.included_fields = set()

        if self.readonly_fields and not (self.all_fields >= self.readonly_fields):
            logger.warning(
                'Readonly fields %s are not present in form fields' % (self.readonly_fields - self.all_fields))
            self.readonly_fields = set()

        if self.ordered_fields and not (self.all_fields >= set(self.ordered_fields)):
            logger.warning(
                'Readonly fields %s are not present in form fields' % (set(self.ordered_fields) - self.all_fields))
            self.ordered_fields = []

        if self.included_fields | self.excluded_fields:
            logger.warning(
                'Included and excluded fields have following fields %s in common' % (
                        set(self.ordered_fields) - self.all_fields
                )
            )
            self.excluded_fields = set()
            self.included_fields = set()

        # Extend exclude list from include list
        self.excluded_fields |= (self.included_fields - self.all_fields)

        if not self.ordered_fields:
            if hasattr(self.form.fields, 'keyOrder'):
                self.ordered_fields = self.form.fields.keyOrder
            else:
                self.ordered_fields = self.form.fields.keys()

        self.fields = []

        # Construct ordered field list considering exclusions
        for field_name in self.ordered_fields:
            if field_name in self.excluded_fields:
                continue

            self.fields.append(field_name)

        # Validate fieldset
        fieldset_fields = set()
        if self.fieldsets:
            for fieldset_name, fieldsets_data in self.fieldsets:
                if 'fields' in fieldsets_data:
                    fieldset_fields |= set(fieldsets_data['fields'])

        if not (self.all_fields >= fieldset_fields):
            logger.warning('Following fieldset fields are invalid %s' % (fieldset_fields - self.all_fields))
            self.fieldsets = {}

        if not (set(self.fields) >= fieldset_fields):
            logger.warning('Following fieldset fields are excluded %s' % (fieldset_fields - set(self.fields)))
            self.fieldsets = {}

    def as_dict(self):
        """
        Returns a form as a dictionary that looks like the following:

        form = {
            'non_field_errors': [],
            'label_suffix': ':',
            'is_bound': False,
            'prefix': 'text'.
            'fields': {
                'name': {
                    'type': 'type',
                    'errors': {},
                    'help_text': 'text',
                    'label': 'text',
                    'initial': 'data',
                    'max_length': 'number',
                    'min_length: 'number',
                    'required': False,
                    'bound_data': 'data'
                    'widget': {
                        'attr': 'value'
                    }
                }
            }
        }
        """
        form_dict = OrderedDict(
            csrf_token=self.csrf_token,
            title=self.form.__class__.__name__,
            non_field_errors=self.form.non_field_errors(),
            label_suffix=self.form.label_suffix,
            is_bound=self.form.is_bound,
            prefix=self.form.prefix,
            fields=OrderedDict(),
            errors=self.form.errors,
            fieldsets=getattr(self.form, 'fieldsets', []),
            ordered_fields=self.fields  # If there are no fieldsets, specify order
        )
        if hasattr(self.form.__class__, '_meta') and hasattr(self.form.__class__._meta, 'model'):
            form_dict['model_name'] = self.form.__class__._meta.model.__name__.lower()
            form_dict['verbose_name'] = self.form.__class__._meta.model._meta.verbose_name

        initial_data = dict()
        for name, field in [(x, self.form.fields[x]) for x in self.fields]:
            # Retrieve the initial data from the form itself if it exists so
            # that we properly handle which initial data should be returned in
            # the dictionary.

            # Please refer to the Django Form API documentation for details on
            # why this is necessary:
            # https://docs.djangoproject.com/en/dev/ref/forms/api/#dynamic-initial-values
            form_initial_field_data = self.form.initial.get(name)

            # Instantiate the Remote Forms equivalent of the field if possible
            # in order to retrieve the field contents as a dictionary.
            remote_field_class_name = 'Remote%s' % field.__class__.__name__
            try:
                remote_field_class = getattr(fields, remote_field_class_name)
                remote_field = remote_field_class(field, form_initial_field_data, field_name=name)
            except Exception as e:
                print('Error serializing field %s: %s', remote_field_class_name, str(e))
                logger.warning('Error serializing field %s: %s', remote_field_class_name, str(e))
                field_dict = {}
            else:
                field_dict = remote_field.as_dict()

            if name in self.readonly_fields:
                field_dict['readonly'] = True

            form_dict['fields'][name] = field_dict

            # fieldsets
            if form_dict['fieldsets'] and name not in form_dict['fieldsets']['fields']:
                form_dict['fieldsets']['fields'].append(name)
            if form_dict['fieldsets'] and name not in form_dict['fieldsets']['labels'].keys():
                form_dict['fieldsets']['labels'][name] = field.label

            # Load the initial data, which is a conglomerate of form initial and field initial
            if 'initial' not in form_dict['fields'][name]:
                form_dict['fields'][name]['initial'] = None

            initial_data[name] = form_dict.get('fields', {}).get(name, {}).get('initial', '')

            if form_dict['fields'][name]['class'] == 'ModelChoiceField' and initial_data[name]:
                initial_data[name] = int(initial_data[name])
            elif form_dict['fields'][name]['class'] == 'ModelMultipleChoiceField':
                initial_data[name] = initial_data[name] or []
                initial_data[name] = [i.id for i in initial_data[name]]
                form_dict['fields'][name]['initial'] = initial_data[name]

        form_dict['data'] = initial_data
        if self.form.data:
            form_dict['data'] = self.form.data

        print('\nDATA', form_dict['data'])

        return form_dict  # resolve_promise(form_dict)
