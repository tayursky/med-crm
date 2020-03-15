import calendar
import decimal
import json
from datetime import date, datetime, timedelta

from django.db.models import Q
from django.views.generic import View, ListView
from django.views.generic.edit import FormView
from django.utils.translation import ugettext as _
from django.http import HttpResponse, JsonResponse
from django.middleware import csrf
from django.shortcuts import render, render_to_response
from django.forms.models import modelform_factory, modelformset_factory, inlineformset_factory
from django.views.decorators.csrf import csrf_exempt

from absolutum.mixins import CoreMixin
from absolutum.settings import DATETIME_FORMAT, TIME_FORMAT
from company.forms import TimeGroupForm
from company.models import Branch, User, TimeTable, TimeGroup
from deal.models import Deal, Service
from directory.forms import DirectoryForm
from identity.models import Person
from identity.utils import LoginRequiredMixin
from utils.date_time import delta_minutes
from utils.choices import filters_choices, get_choices
from utils.remote_forms.forms import RemoteForm
from utils.normalize_data import normalise_data


class TimeGroupView(FormView):
    model = TimeGroup
    branch = None
    timezone = 0
    group = None
    action = None
    permissions = []
    template_name = 'debug.jinja2'

    def dispatch(self, request, *args, **kwargs):
        self.permissions = self.model.get_permissions(self.request)
        self.action = kwargs.get('action')
        self.action = 'change' if self.action == 'save' else self.action
        try:
            self.group = self.model.objects.get(pk=kwargs.get('pk'))
        except self.model.DoesNotExist:
            pass
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):
        kwargs = self.get_form_kwargs()
        kwargs.update(dict(
            initial=self.kwargs
        ))
        initial = json.loads(self.request.GET.get('initial', '{}'))
        initial.update(dict(request=self.request))
        kwargs['initial'].update(initial)

        if 'data' in kwargs:
            kwargs['data'] = normalise_data(self.model, kwargs['data'])

        form = TimeGroupForm(**kwargs)
        if self.group:
            form = TimeGroupForm(instance=self.group, **kwargs)

        return form

    def post(self, request, *args, **kwargs):
        if self.action not in self.permissions:
            return HttpResponse('no perm')

        if self.action == 'delete':
            self.group.delete()
            context = dict(
                deleted=True,
                message=dict(type='success', text='Удалено'),
            )
            return JsonResponse(context)

        form = self.get_form()
        if form.is_valid():
            form.save()
            self.group = form.instance
            context = dict(
                id=self.group.id,
                message=dict(type='success', text='Сохранено')
            )
            return JsonResponse(context)
        else:
            return JsonResponse(dict(
                form=dict(errors=form.errors)
            ))

    def get(self, request, *args, **kwargs):
        _form = RemoteForm(self.get_form(), model=self.model, csrf_token=csrf.get_token(self.request)).as_dict()
        context = dict(
            title=self.group.__str__() if self.group else 'Новая группа',
            form=_form,
            permissions=self.permissions
        )

        if self.request.GET.get('debug'):
            return render_to_response('debug.jinja2', locals())
        return JsonResponse(context)
