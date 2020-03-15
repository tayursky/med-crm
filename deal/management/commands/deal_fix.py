# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from deal.models import Deal


class Command(BaseCommand):
    help = 'fix deals'

    def handle(self, *args, **options):
        print('Begin fix for deals\n')

        # Deal.objects.filter(service_type=None).update(service_type=1)
        # Deal.objects.filter(status='cancelled').update(status='reject')

        for deal in Deal.objects.filter(comment__icontains='Возвраст'):
            print(deal.comment, '\n')
            deal.comment = deal.comment.replace('Возвраст', 'Возраст')
            deal.save()

        print('End fix')
