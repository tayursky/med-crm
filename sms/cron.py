# -*- coding: utf-8 -*-

from sms.management.commands.sms_remind_1day import Command as Sms_remind_1day
from sms.management.commands.sms_send import Command as Sms_scheduled


def sms_scheduled():
    cmd = Sms_scheduled()
    cmd.handle()


def sms_remind():
    cmd = Sms_remind_1day()
    cmd.handle()
