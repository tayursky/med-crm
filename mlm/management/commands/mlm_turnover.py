# -*- coding: utf-8 -*-

from decimal import Decimal

from datetime import datetime, timedelta
from django.core.management.base import BaseCommand, CommandError

from mlm.models import Agent, AgentTurnover, Invite


class Command(BaseCommand):
    help = 'check invites'

    def handle(self, *args, **options):
        print('\nStart mlm calculate turnover')

        turnovers = []
        for agent in Agent.objects.filter(position='manager'):
            manager_income, data = agent.calculate_turnover()
            turnovers += data
            agent.cache.update(dict(
                manager_income=str(manager_income),
                total=str(Decimal(agent.cache.get('invite_cost')) + manager_income)
            ))
            agent.save()
            print(agent.person.last_name, manager_income)

        AgentTurnover.objects.all().delete()
        AgentTurnover.objects.bulk_create([AgentTurnover(**data) for data in turnovers])

        print('\nEnd mlm calculate turnover\n')
