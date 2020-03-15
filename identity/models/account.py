from django.contrib.auth.models import AbstractUser, PermissionsMixin, UserManager, Group as AuthGroup
from django.db import models
from simple_history.models import HistoricalRecords


class Account(AbstractUser):
    first_name = None
    last_name = None
    date_joined = None
    last_login = None

    history = HistoricalRecords()

    def get_full_name(self):
        return self.person.get_full_name_display() if self.person else ''

    def get_short_name(self):
        return self.person.first_name if self.person else ''

    def get_person(self):
        return self.person or None
