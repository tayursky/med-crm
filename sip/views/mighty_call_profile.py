# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import json
import requests
import hashlib

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import View, DetailView, ListView, TemplateView
from django.forms import models as model_forms

from absolutum.settings import MIGHTY_CALL_SET
from sip.models import Log, MightyCallUser
from sip.views.mighty_call import MightyCall
from utils.clean_data import get_numbers


class ParseProfile(LoginRequiredMixin, View):
    """
        Заполняем информацию о пользователях MightyCall
    """
    params = dict()
    permissions = []

    def dispatch(self, request, *args, **kwargs):
        self.params['person'] = self.request.user.person if self.request.user.person else None
        return super(ParseProfile, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        telephony = MightyCall(params=self.params)

        for profile_q in MightyCallUser.objects.all():
            profile, errors = telephony.get_profile(extension_number=profile_q.extension_number)
            if profile:
                profile_q.name = '%s %s' % (profile.get('firstName'), profile.get('lastName'))
                profile_q.save()

        context = dict(
            answer='done',
        )

        if request.GET.get('debug'):
            from django.shortcuts import render_to_response
            return render_to_response('debug.jinja2', locals())
        return JsonResponse(context, safe=False)
