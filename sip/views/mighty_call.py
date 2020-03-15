# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import json
import requests
import hashlib

from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import View, DetailView, ListView, TemplateView
from django.forms import models as model_forms

from absolutum.settings import MIGHTY_CALL_SET
from sip.models import Log
from utils.clean_data import get_numbers


class MightyCall():
    """
        MightyCall
    """
    base_url = 'https://api.yandex.mightycall.ru/{prefix}/{version}/'
    params = dict()
    person = None
    mighty_user = None
    api_key = None
    errors = dict()
    display_number = '+74951442323'

    def __init__(self, *args, **kwargs):
        self.base_url = self.base_url.format(
            prefix=MIGHTY_CALL_SET['prefix'],
            version=MIGHTY_CALL_SET['version'],
        )
        self.params = kwargs.get('params')

        self.person = self.params.get('person')
        self.mighty_user = self.params.get('mighty_user')
        self.api_key = MIGHTY_CALL_SET['api_key']

    def get_headers(self, user):
        return {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': 'Bearer %s' % user['token'],
            'x-api-key': self.api_key
        }

    def ping(self):
        """
            Метод возвращает текущий статус MightyCall API
        """
        url = self.base_url + 'auth/ping/'
        rq = requests.get(url)
        log = Log.objects.create(
            event_type='ping',
            data=dict(status_code=rq.status_code, reason=rq.reason),
            from_number='sip',
        )
        # return rq.reason == 'OK'
        return log.id, self.errors

    def get_user(self, refresh=False):
        """
            Метод возвращает пользователя с авторизационным токеном, необходимым для доступа к API
        """
        url = self.base_url + 'auth/token/'
        print('\nurl', url)
        data = dict()
        user_values = ['name', 'extension_number', 'user_key', 'display_number',
                       'token', 'token_type', 'token_expires', 'refresh_token']
        if not self.mighty_user:
            self.mighty_user = self.person.mighty_call_user if self.person else None
        if not self.mighty_user:
            self.errors['mighty_call_user'] = 'Нет пользователя яндекс телефонии'

        if not self.mighty_user.token or refresh:
            print('\nno token\n')
            data = {
                'grant_type': 'client_credentials',
                'client_id': '%s' % self.api_key,
                'client_secret': '%s' % self.mighty_user.user_key,
            }

        elif self.mighty_user.token_expires and self.mighty_user.token_expires <= datetime.now() - timedelta(minutes=1):
            print('\ntoken expired\n')
            data = {
                'grant_type': 'refresh_token',
                'refresh_token': '%s' % self.mighty_user.refresh_token
            }

        if data and not self.errors:
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'x-api-key': '%s' % self.api_key
            }
            rq = requests.post(url, headers=headers, data=data)
            rq_content = json.loads(rq.content.decode('utf-8'))
            self.mighty_user.token = rq_content.get('access_token')
            self.mighty_user.token_type = rq_content.get('token_type')
            self.mighty_user.token_expires = datetime.now() + timedelta(seconds=rq_content.get('expires_in', 0))
            self.mighty_user.refresh_token = rq_content.get('refresh_token')
            self.mighty_user.save()
            log = Log.objects.create(
                event_type=data['grant_type'],
                data=dict(
                    status_code=rq.status_code,
                    reason=rq.reason,
                    content=rq_content
                ),
            )
        user = {i: getattr(self.mighty_user, i) for i in user_values}
        return user, self.errors

    def make_call(self):
        """
            Метод инициирует звонок
        """
        url = self.base_url + 'calls/makecall/'
        print('\nurl', url)
        phone = get_numbers(self.params.get('phone'))
        if not phone:
            self.errors['phone'] = 'Номер отсутствует'
        user, errors = self.get_user()
        headers = self.get_headers(user)
        data = {
            'from': self.display_number,
            'to': '+%s' % phone,
        }
        log = Log.objects.create(
            event_type='make_call', to_number=phone
        )
        rq = requests.post(url, headers=headers, data=data)
        rq_content = json.loads(rq.content.decode('utf-8'))
        print('rq_content', rq_content)

        log.from_number=rq_content['data']['caller']['name']
        log.data=dict(
                data=data,
                status_code=rq.status_code,
                reason=rq.reason,
                content=rq_content,
            )
        log.save()
        return log.id, self.errors

    def phone_numbers(self):
        """
            Метод возвращает: список рабочих номеров в аккаунте, данные о конкретном рабочем номере
        """
        url = self.base_url + 'phonenumbers/{phone_number}'.format(phone_number='74950088376')
        print('\nurl', url)
        user, errors = self.get_user()
        headers = self.get_headers(user)
        rq = requests.get(url, headers=headers)
        rq_content = json.loads(rq.content.decode('utf-8'))
        log = Log.objects.create(
            event_type='phone_numbers',
            from_number=user['name'],
            data=dict(
                status_code=rq.status_code,
                reason=rq.reason,
                content=rq_content,
            )
        )
        return log.id, self.errors

    def get_profile(self, extension_number=None):
        """
            Метод возвращает информацию о текущем пользователе,
            либо пользователе с указанным добавочным номером extension
        """
        user, errors = self.get_user()
        extension_number = extension_number if extension_number else user['extension_number']
        url = self.base_url + 'profile/%s' % extension_number
        print('\nurl', url)
        headers = self.get_headers(user)
        rq = requests.get(url, headers=headers)
        rq_content = json.loads(rq.content.decode('utf-8'))
        print('rq_content', rq_content)
        log = Log.objects.create(
            event_type='get_profile',
            from_number=user['name'],
            data=dict(
                status_code=rq.status_code,
                reason=rq.reason,
                content=rq_content
            )
        )
        return rq_content.get('data'), self.errors

    def get_status(self):
        """
            Метод возвращает статус доступности текущего пользователя
        """
        url = self.base_url + 'profile/status'
        print('\nurl', url)
        user, errors = self.get_user()
        headers = self.get_headers(user)
        rq = requests.get(url, headers=headers)
        rq_content = json.loads(rq.content.decode('utf-8'))
        log = Log.objects.create(
            event_type='get_status',
            from_number=user['name'],
            data=dict(
                status_code=rq.status_code,
                reason=rq.reason,
                content=rq_content
            )
        )
        return log.id, self.errors

    @staticmethod
    def print_dic(name, item):
        print('%s' % name.upper())
        if type(item) == 'str':
            item = json.loads(item, {})
        for key, value in item.items():
            print('%s = %s' % (key, value))
