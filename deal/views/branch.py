from datetime import date, datetime, timedelta
import decimal

from django.db.models import Q
from django.http import JsonResponse
from django.views.generic import ListView
from django.shortcuts import render, render_to_response

from absolutum.mixins import CoreMixin, DisplayMixin
from identity.utils import LoginRequiredMixin
from company.models import Branch, Master
from deal.models import Deal, Service
from utils.date_time import delta_minutes, get_week_start
from utils.choices import get_choices, filters_choices


class BranchList(LoginRequiredMixin, ListView):
    """
        Список филиалов
    """
    model = Branch
    user = None
    person = None
    query = None
    permissions = []

    def dispatch(self, request, *args, **kwargs):
        self.user = request.user
        self.person = self.user.person
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        # if 'view' not in self.permissions:
        #     return JsonResponse(dict(answer='No permissions'), safe=False)

        self.queryset = self.get_queryset()

        if not self.user.has_perm('Администраторы') and self.person:
            self.queryset = self.queryset.filter(Q(managers=self.person) | Q(workers=self.person))

        ordered = []
        branches = dict()
        masters = dict()
        services = dict()
        group_services = dict()

        for branch in self.queryset.select_related('city') \
                .prefetch_related('workers', 'workers__account', 'workers__account__groups'):
            ordered.append(branch.id)
            branches[branch.id] = dict(
                id=branch.id,
                label='%s (%s)' % (branch.city.name, branch.name),
                masters=[i.id for i in branch.workers.all()],
                group_services=[],
                services=[],
            )
            print([i.id for i in branch.workers.all()])

        for master in Master.objects \
                .filter(worker_branches__in=[key for key in branches.keys()]) \
                .prefetch_related('services'):
            masters[master.id] = dict(
                id=master.id,
                full_name=master.cache.get('full_name', ''),
                group_services=[],
                services=[i.id for i in master.services.all()],
            )

        for service in Service.objects.filter(masters__in=[key for key in masters.keys()]).select_related('group'):
            group_services[service.group.id] = dict(name=service.group.name)
            services[service.id] = dict(
                id=service.id,
                name=service.name,
                group=service.group.id,
            )

        # Удаляем workers из masters
        for branch_id in ordered:
            print('\n', branches[branch_id]['masters'])
            for user_key in branches[branch_id]['masters'].copy():
                if user_key not in masters.keys():
                    branches[branch_id]['masters'].remove(user_key)
                    print('DELETE', user_key)
                else:
                    print(user_key)

        for master_key, master in masters.items():
            for service_id in master['services']:
                master['group_services'].append(services[service_id]['group'])
            master['group_services'] = list(set(master['group_services']))

            for branch_key, branch in branches.items():
                if master_key in branch['masters']:
                    branch['services'] += master['services']
                    branch['group_services'] += master['group_services']
                branch['services'] = list(set(branch['services']))
                branch['group_services'] = list(set(branch['group_services']))

        context = {
            'ordered': ordered,
            'branches': branches,
            'masters': masters,
            'services': services,
            'group_services': group_services
        }

        if self.request.GET.get('debug'):
            return render_to_response('debug.jinja2', locals())
        return JsonResponse(context, safe=False)
