# -*- coding: utf-8 -*-

from sip.management.commands.sip_refresh_token import Command as SipRefreshToken


def sip_refresh_token():
    cmd = SipRefreshToken()
    cmd.handle()
