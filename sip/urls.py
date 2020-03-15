# from periods.period import TimeInterval as Period
from django.urls import path
from django.shortcuts import redirect

from sip.views.call import SipEvent
from sip.views.mango import MangoCall
from sip.views.mighty_call_hook import MightyCallWebHook
from sip.views.mighty_call_profile import ParseProfile
from sip.views.event import SipLog, GetIncoming

urlpatterns = [
    path('get_incoming/', GetIncoming.as_view(), name='get_incoming'),

    path('mightycall/webhook/', MightyCallWebHook.as_view(), name='mighty_webhook'),
    path('mightycall/parse_profiles/', ParseProfile.as_view(), name='mighty_parse_profiles'),

    # path('<str:event>/', MangoCall.as_view(), name='mango_event'),
    path('<str:event>/', SipEvent.as_view(), name='sip_event'),

    path('events/<str:event>', SipLog.as_view(), name='sip_log'),
]
