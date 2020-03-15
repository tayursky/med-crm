import json
from datetime import date, datetime

from django.core.exceptions import FieldDoesNotExist
from django.db.models import Q
from collections import Iterable


# from utils.choices import get_choices


class CoreMixin(object):

    def get_bread_crumbs(self):
        data = []
        _obj = self
        while _obj:
            data.insert(0, {
                'id': _obj.id,
                'model_name': _obj._meta.model.__name__.lower(),
                'model_label': _obj._meta.verbose_name,
                'label': _obj.__str__(),
                'url': _obj.get_absolute_url()
            })
            _obj = _obj.get_parent_object()
        return data

    def get_parent_name(self):
        return getattr(self, 'parent_name', None)

    def get_parent_object(self):
        return getattr(self, self.get_parent_name()) if self.get_parent_name() else None

    @classmethod
    def get_permissions(cls, request, full_label=False):
        """
            Получаем права доступа
        """
        perms = []
        for perm in request.user.get_all_permissions():
            app_label, _perm = perm.split('.')
            if app_label == cls._meta.app_label:
                if full_label:
                    perms.append(perm)
                else:
                    action, object_name = _perm.split('_')
                    if object_name == cls._meta.object_name.lower():
                        print(object_name)
                        perms.append(action)
        return perms

    @classmethod
    def get_filters(cls, request, filters=None):
        """
            Получаем словарь фильтров
        """
        filters = filters if filters else dict()
        filters_fields = filters.get('fields', getattr(cls, 'filters_fields', dict()))
        filters = dict(
            data=filters.get('data', getattr(cls, 'filters_data', dict())),
            ordered=filters.get('ordered', getattr(cls, 'filters_ordered', [])),
            fields=dict()
        )
        filters_exclude = []

        for key in filters['ordered']:
            if key not in filters_fields:
                filters_exclude.append(key)
                continue
            filters['fields'][key] = filters_fields.get(key, dict())
            if key not in filters['data']:
                filters['data'][key] = None

            try:
                filters['data'][key] = json.loads(request.GET.get(key, filters['data'][key]))
            except (TypeError, json.decoder.JSONDecodeError):
                filters['data'][key] = request.GET.get(key, filters['data'][key])

            if filters['fields'][key]['widget'].get('input_type') in ['checkbox'] or \
                    filters['fields'][key]['widget']['attrs'].get('boolean'):
                if filters['data'][key] in [True, 'true']:
                    filters['data'][key] = True
                elif filters['data'][key] in [False, 'false']:
                    filters['data'][key] = False

            elif filters['data'][key] in [True, 'true']:
                filters['data'][key] = True
            elif filters['data'][key] in [False, 'false']:
                filters['data'][key] = False

            elif filters['fields'][key]['widget'].get('input_type') in ['select']:
                try:
                    filters['data'][key] = int(filters['data'][key])
                except (ValueError, TypeError):
                    pass

        filters['ordered'] = [i for i in filters['ordered'] if i not in filters_exclude]

        return filters

    @classmethod
    def get_filters_q(cls, request, filters=None, get_dict=None):
        """
            Получаем фильтр в виде Q-объекта
        """
        filters = filters if filters else cls.get_filters(request, filters)
        q = Q()
        q_kwargs = dict()
        for key, field in filters['fields'].items():
            if field['widget'].get('input_type') == 'daterange':
                try:
                    _range = json.loads(request.GET.get(key))
                except TypeError:
                    continue
                try:
                    dt_range_start = datetime.strptime(_range[0], '%d.%m.%Y')
                    dt_range_finish = datetime.strptime(_range[1], '%d.%m.%Y').replace(hour=23, minute=59)
                except (IndexError, TypeError):
                    continue
                kwargs = {
                    ('%s__gte' % key): dt_range_start, ('%s__lte' % key): dt_range_finish
                }
                if get_dict:
                    q_kwargs.update(kwargs)
                q &= Q(**kwargs)
                filters['data'][key] = [_range[0], _range[1]]
                continue

            try:
                filters['data'][key] = json.loads(request.GET.get(key))
            except (TypeError, json.decoder.JSONDecodeError):
                pass

            if filters['data'][key] or filters['data'][key] is False:
                q_key = field['key']
                if filters['data'][key] in ['', 'null']:
                    continue
                if field.get('postfix'):
                    q_key = '%s__%s' % (field['key'], field['postfix'])
                kwargs = {q_key: filters['data'][key]}
                if get_dict:
                    q_kwargs.update(kwargs)
                q &= Q(**kwargs)

        if get_dict:
            return q_kwargs
        return q

    @classmethod
    def get_filter_fields(cls):
        """
            Получаем список фильтров
        """
        result = []
        for item in getattr(cls, 'filters_ordered', []):
            filter_name = item[0] if isinstance(item, tuple) else item
            result.append(filter_name)
        return result

    @classmethod
    def has_data(cls, filters):
        """
            Проверяем есть ли данные для фильтров
        """
        # if item['widget']['input_type'] == 'daterange':
        #     key += '[]'
        # if self.request.GET.get(key):
        #     request_dict[key] = self.request.GET.get(key)

        result = []
        for item in getattr(cls, 'filters_ordered', []):
            filter_name = item[0] if isinstance(item, tuple) else item
            result.append(filter_name)
        return result


class DisplayMixin(object):
    list_display = []
    display_labels_map = {}
    base_dt_hidden = ['id', 'Model']
    datatable_hidden = base_dt_hidden

    dt_subqueries = []
    dt_related = []

    list_form_fields = []
    filter_fields = []
    primary_info_fields = []
    card_fields = []

    base_actions = (
        # {'name': 'delete', 'label': 'Удалить', 'target': 'instance'},
        # {'name': 'edit', 'label': 'Редактировать', 'target': 'instance'},
        {'name': 'create', 'label': 'Добавить', 'target': 'model'},
    )

    short_name = None

    def get_actions(self, *args, **kwargs):
        return dict(edit='wqeqwe', url='ewrwer')

    @classmethod
    def get_headers(cls, fields=None, exclude=None):
        if not fields:
            fields = cls.list_display
        if exclude and isinstance(exclude, Iterable):
            return list(filter(lambda e: e not in exclude, fields))

        ordering = {}
        meta = getattr(cls, '_meta', None) or getattr(cls, 'Meta', None)
        meta_ordering = getattr(meta, 'ordering', [])
        for order in meta_ordering:
            if order[0] == '-':
                ordering[order[1:]] = 'desc'
            else:
                ordering[order] = 'asc'

        fields_list = []
        for field in fields:
            item = {
                'value': field,
                'order': ordering.get(field, None)
            }
            if field in cls.display_labels_map:
                item['text'] = cls.display_labels_map[field]
            elif '__' in field:
                c = cls
                for fname in field.split('__')[:-1]:
                    c = getattr(c, fname)
                _field_name = field.split('__')[-1]
                item['text'] = c.field.related_model._meta.get_field(_field_name).verbose_name
            else:
                item['text'] = cls._meta.get_field(field).verbose_name

            fields_list.append(item)

        return fields_list
