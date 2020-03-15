# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand, CommandError

from mlm.models import Agent, Invite


class Command(BaseCommand):
    help = 'check invites'

    def handle(self, *args, **options):
        print('\nStart mlm charge')
        # after_delay = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=14)
        # print(after_delay)
        # for invite in Invite.objects.filter(status='wait', deal__finish_datetime__lt=after_delay):
        for invite in Invite.objects.all():
            print(invite)
            invite.status = 'ok'
            invite.save()

        for agent in Agent.objects.all():
            agent.save()

        # Invite.objects.all().update(status='ok')

        print('\nEnd mlm charge\n')
