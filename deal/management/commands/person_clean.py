# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from deal.models import Deal
from identity.models import Person


class Command(BaseCommand):
    help = 'clean persons'

    def handle(self, *args, **options):
        print('Begin clean persons\n')
        exclude_persons = []

        for person in Person.objects.all():
            if not person.rel_deals.all().exists() and not person.account:
                print('person', person.id, person, person.get_phone_str_display())
                # print('person.account', person.account)
                person.delete()

        # for person in Person.objects.all():
        #     exclude_persons.append(person.id)
        #     duplicate = Person.objects \
        #         .filter(first_name=person.first_name,
        #                 patronymic=person.patronymic,
        #                 last_name=person.last_name,
        #                 birthday=person.birthday) \
        #         .exclude(pk__in=exclude_persons)
        #     for dup in duplicate:
        #         print('duplicate: %s %s (%s)' % (person.id, dup, dup.id))
        #         if not dup.rel_deals.all().exists() and not dup.account:
        #             dup.delete()
        #         elif not person.rel_deals.all().exists() and not person.account:
        #             person.delete()
        #
        #         for deal in dup.rel_deals.all():
        #             print('deal', deal)
        #         print('\n')
        #
        # print('End clean persons')
