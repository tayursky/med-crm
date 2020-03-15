import json

from django.apps import apps
from django.db.models import Q


def get_choices(request, obj=None, get_list=False):
    user = request.user
    choices = []
    try:
        model = apps.get_model(obj)
    except (ValueError, LookupError):
        model = None
    try:
        person_id = user.person.id
    except AttributeError:
        person_id = None

    if obj == 'company.Branch':
        model = apps.get_model('company.Branch')
        branch_qs = model.objects.none()
        if user.has_perm('Администраторы'):
            branch_qs = model.objects.all()
        elif person_id:
            branch_qs = model.objects.filter(Q(managers=person_id) | Q(workers=person_id))

        for branch in branch_qs.distinct():
            choices.append(dict(label=branch.__str__(), value=branch.id))

    elif obj == 'deal.Service':
        model = apps.get_model('deal.Service')
        service_q = model.objects.none()
        if user.has_perm('Администраторы'):
            service_q = model.objects.all().distinct()
        elif person_id:
            service_q = model.objects.filter(masters=person_id).prefetch_related('branch').distinct()

        elif obj == 'deal.Service':
            for service in service_q:
                choices.append(dict(label=service.__str__(), value=service.id))

    elif obj == 'deal_status':
        model = apps.get_model('deal.Deal')
        for status in model.DEAL_STATUS:
            choices.append(dict(label=model.DEAL_STATUS_NAME[status[0]], value=status[0]))

    if not choices and model:
        if user.has_perm('Администраторы'):
            choices = [dict(label=i.__str__(), value=i.id) for i in model.objects.all().distinct()]
        else:
            choices = [dict(label=i.__str__(), value=i.id) for i in model.objects.all().distinct()
                       if not getattr(i, 'hidden', None)]
    if get_list:
        choices = [i['value'] for i in choices]

    return choices


def filters_choices(request, filters, model):
    user = request.user
    for field_key, field in filters['fields'].items():
        model_name = field['widget'].get('model_name', None)
        choices = field['widget'].get('choices', None)
        if model_name:
            field['widget']['choices'] = get_choices(request, model_name)
        elif type(choices).__name__ == 'ModelBase':
            if user.has_perm('Администраторы'):
                field['widget']['choices'] = [dict(label=i.__str__(), value=i.id)
                                              for i in choices.objects.all().distinct()]
            else:
                field['widget']['choices'] = [dict(label=i.__str__(), value=i.id)
                                              for i in choices.objects.all().distinct()
                                              if not getattr(i, 'hidden', False)]
        # Attrs
        for attr_key, attrs in field['widget'].get('attrs', {}).items():
            for field_name, attr in attrs.items():
                related_field = getattr(model, field_key)
                try:
                    related_model = related_field.field.related_model
                except AttributeError:
                    related_model = None
                if attr_key == 'relations' and related_model:
                    relations = dict()
                    for rel_key, rel_name in attrs.items():
                        if type(rel_name).__name__ == 'str':
                            relations[rel_key] = dict()
                            related_name = getattr(related_model, rel_name).field.related_query_name()
                            for obj in getattr(related_model, rel_name).field.related_model.objects.all():
                                relations[rel_key][obj.id] = \
                                    [i['id'] for i in getattr(obj, related_name).all().values('id')]
                    attr = dict(relations=relations) if relations else None
                if attr:
                    filters['fields'][field_key]['widget']['attrs'] = attr

    return filters
