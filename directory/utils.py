from django.apps import apps
from django.core.exceptions import AppRegistryNotReady, ObjectDoesNotExist, FieldDoesNotExist
from django.urls import reverse_lazy

MODEL_MAPPING = dict(map(lambda m: (m.__name__.lower(), m), apps.get_models()))


def get_model(model_name):
    model_name = model_name.lower() if model_name else None
    if model_name in MODEL_MAPPING:
        return MODEL_MAPPING[model_name]
    return None


def get_menu_items(list):
    for index, item in enumerate(list):
        subitems = []
        for subitem in item.get('subitems', []):
            if subitem.get('model'):
                model = subitem.get('model')
                subitem.pop('model', None)
                subitem.update(dict(
                    perm=subitem.get('perm', '%s.view_%s' % (model._meta.app_label, model.__name__.lower())),
                    router_name=subitem.get('router_name') or getattr(model, 'router_name', 'directory_list'),
                    label=model._meta.verbose_name_plural,
                    params=dict(model_name=model.__name__.lower()),
                    icon=getattr(model, 'icon', '')
                ))
                subitem['url'] = subitem.get('url', reverse_lazy('directory:model_list',
                                                                 kwargs={'model_name': model.__name__.lower()}))
            subitems.append(subitem)
        list[index]['subitems'] = subitems

    return list


def get_child_list(obj):
    child_list = []
    if not obj:
        return child_list
    for item in getattr(obj._meta.model, 'child_list', []):
        if item == 'detail':
            elem = {
                'name': obj._meta.verbose_name,
                'url': reverse_lazy('directory:model_detail', kwargs={
                    'model_name': obj._meta.model.__name__.lower(), 'pk': obj.id
                }),
            }
        else:
            _, name = get_linked_obj(obj._meta.model, item)
            elem = {
                'name': name,
                'url': reverse_lazy('directory:model_relation_list',
                                    kwargs=dict(
                                        parent_model_name=obj._meta.model.__name__.lower(),
                                        parent_pk=obj.pk,
                                        related_name=item
                                    )),
            }
        child_list.append(elem)
    return child_list


def get_linked_obj(parent, link='string'):
    obj = parent
    name, fname = None, None

    for fname in link.split('.'):
        try:
            field = obj._meta.get_field(fname)
            name = field.verbose_name if hasattr(field, 'verbose_name') else None
            obj = field.related_model
        except FieldDoesNotExist:
            try:
                obj = getattr(obj, fname)
                if hasattr(obj, 'model'):
                    obj = obj.model
            except ObjectDoesNotExist:
                obj = None
    if not obj:
        try:
            field = parent._meta.get_field(fname)
            name = field.verbose_name
            obj = field.related_model
        except FieldDoesNotExist:
            return None, None

    if hasattr(obj, 'model'):
        obj = obj.model

    if not name:
        try:
            name = obj.short_name or obj._meta.verbose_name_plural
        except:
            name = obj.field.verbose_name

    return obj, name


def get_detail_fields_mapping(obj):
    resullt = []
    list_detail_fields = getattr(obj, 'list_detail_fields', [])
    for item in list_detail_fields:
        _obj = obj
        field = None
        display_labels_map = getattr(obj, 'display_labels_map', {})
        label = display_labels_map.get(item, None)
        for field in item.split('__'):
            if not label:
                label = _obj._meta.get_field(field).verbose_name
            _obj = getattr(_obj, field, None)

        if field:
            resullt.append({
                'name': item,
                'label': label,
                'value': _obj
            })
    return resullt
