# from periods.period import TimeInterval as Period
from django.urls import path
from django.shortcuts import redirect

from mlm.views.calculate import CalculateView
from mlm.views.check import CheckView
from mlm.views.invite import InviteView, InviteSend
from mlm.views.agent_cabinet import AgentCabinetView

urlpatterns = [
    path('calculate/', CalculateView.as_view(), name='calculate'),
    path('check/', CheckView.as_view(), name='check'),

    # path('invite/<str:token>/', InviteView.as_view(), name='invite'),
    path('invite_send/', InviteSend.as_view(), name='invite_send'),

    # path('account/', AgentCabinetView.as_view(), name='mlm_agent'),
]
