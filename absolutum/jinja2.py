from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import reverse

from jinja2 import Environment


def resource_as_string(name, charset='utf-8'):
    with open(name) as f:
        return f.read()


def environment(**options):
    env = Environment(**options)
    env.globals.update(dict(
        static=staticfiles_storage.url,
        url=reverse,
        resource_as_string=resource_as_string,
        debug=True
    ))
    return env
