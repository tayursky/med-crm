import decimal
import json
from datetime import date, datetime, timedelta

from django.db.models import Q
from django.views.generic import ListView
from django.views.generic.edit import View, FormView
from django.shortcuts import render, render_to_response
from django.http import HttpResponse, JsonResponse

from absolutum.settings import DATETIME_FORMAT
from absolutum.mixins import CoreMixin, DisplayMixin
from deal.models import Client, Deal, DealComment
from identity.utils import LoginRequiredMixin
from utils.choices import get_choices, filters_choices


class DealCommentListView(LoginRequiredMixin, ListView, CoreMixin):
    """
        Список комментариев
    """
    model = DealComment
    client = None
    deal = None
    filters = dict()
    filters_q = Q()
    timezone = 0

    def dispatch(self, request, *args, **kwargs):
        self.timezone = request.user.person.timezone
        self.client = self.request.GET.get('client', None)
        self.deal = self.request.GET.get('deal', None)
        self.filters = self.set_filters(request)
        self.filters_q = self.model.get_filters_q(self.request, filters=self.filters)
        return super().dispatch(request, *args, **kwargs)

    def set_filters(self, request):
        filters = dict(
            ordered=['comment'],
            fields=dict(
                comment=dict(label='Комментарий', key='comment__icontains',
                             widget=dict(attrs={}, name='TextInput', input_type='text'))
            )
        )
        filters = self.get_filters(request, filters=filters)
        filters = filters_choices(request, filters, self.model)
        return filters

    def get_queryset(self):
        queryset = self.model.objects.none()
        list_related = getattr(self.model, 'list_related', [])

        if self.client:
            queryset = self.model.objects.filter(Q(client=self.client) | Q(deal__persons=self.client))
        elif self.deal:
            deals = [self.deal]
            deal_q = Deal.objects.get(pk=self.deal)
            for rel_person in deal_q.rel_persons.all():
                for rel_person_deal in rel_person.person.rel_deals.all():
                    deals += [rel_person_deal.deal.id]
            queryset = self.model.objects.filter(Q(deal__in=deals) | Q(client__rel_deals__deal=self.deal))

        elif self.filters_q:
            queryset = self.model.objects \
                .filter(self.get_filters_q(self.request, filters=self.filters))

            # Фильтр только по ответственным филиалам
            if not self.request.user.has_perm('Администраторы'):
                queryset = queryset.filter(Q(deal__service__managers=self.request.user.person.id) |
                                           Q(deal__service__masters=self.request.user.person.id))

        return queryset.select_related(*list_related).distinct()

    def get_comments_list(self):
        comments = []
        values = ['id', 'client_id', 'client__cache', 'deal_id', 'deal__cache', 'comment', 'created_at']
        for comment in self.get_queryset().values(*values):
            item = dict(
                id=comment['id'],
                client=comment['client_id'],
                client__cache=comment['client__cache'],
                deal=comment['deal_id'],
                deal__cache=comment['deal__cache'],
                created_at=(comment['created_at'] + timedelta(hours=self.timezone)).strftime(DATETIME_FORMAT),
                comment=comment['comment'],
            )
            comments.append(item)
        return comments

    def get(self, request, *args, **kwargs):
        if not request.GET:
            return render(request, 'app_vue.jinja2')
        context = dict(
            title='Комментарии',
            filters=self.filters,
            comments=self.get_comments_list(),
        )
        return JsonResponse(context, safe=False)
