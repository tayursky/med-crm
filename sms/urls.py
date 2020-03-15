# from periods.period import TimeInterval as Period
from django.urls import path
from django.shortcuts import redirect

from sms.views.list import SmsList
from sms.views.sms import SmsResendView

urlpatterns = [

    path('', SmsList.as_view(), name='sms_list'),

    path('resend/', SmsResendView.as_view(), name='resend'),



    # path('<str:parent_name>/<int:parent_id>/<str:model_name>/list', views.ListTemplate.as_view(),
    #      name='child_model_list'),

    # path('<str:parent_name>/<str:parent_id>/<str:model_name>/action/<str:action>',
    #      views_forms.ModelActions.as_view(), name='model_action'),

]
