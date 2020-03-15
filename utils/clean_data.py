from django.apps import apps
from django.db.models import Q


def get_numbers(value):
    answer = ''
    for i in str(value):
        try:
            answer += str(int(i))
        except ValueError:
            pass

    return answer


