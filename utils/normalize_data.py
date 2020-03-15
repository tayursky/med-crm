import json
from django.core.exceptions import FieldDoesNotExist


def normalise_phone(data):
    if not data:
        return None

    phone = ''
    for i in str(data):
        try:
            phone += str(int(i))
        except (ValueError, TypeError):
            pass

    if len(phone) == 11 and phone[0] == '8':
        phone = '7' + phone[1:]

    return phone


def normalise_data(model, data):
    answer = dict()
    for field_name, value in data.items():
        answer[field_name] = value
        try:
            if hasattr(model, field_name) \
                    and model._meta.get_field(field_name).get_internal_type() == 'ManyToManyField':
                # try:
                #     answer[field_name] = get_list(value)
                # except ValueError:
                #     continue
                answer[field_name] = model._meta.get_field(field_name).related_model.objects \
                    .filter(pk__in=get_list(value))
                continue
        except FieldDoesNotExist:
            pass

        if isinstance(value, list):
            answer[field_name] = value[0]

    return answer


def get_list(value):
    if not value:
        return ''
    if isinstance(value, list):
        return value
    value = str(value).replace('[', '').replace(']', '')
    return [int(i) for i in value.split(',')] if value else []
