# from periods.period import TimeInterval as Period
from django.urls import path
from django.shortcuts import redirect

from directory.views import forms, list, remote_search, working_calendar

urlpatterns = [
    path('remote_search/<str:model_name>/', remote_search.RemoteSearch.as_view(), name='remote_search'),

    path('mlm_agent/', list.ModelList.as_view(), name='mlm_agent_list', kwargs=dict(model_name='agent')),
    path('working_calendar/', working_calendar.WorkingCalendarView.as_view(), name='working_calendar'),

    path('<str:model_name>/', list.ModelList.as_view(), name='model_list'),
    path('<str:model_name>/<int:pk>/', list.ModelDetail.as_view(), name='model_detail'),
    path('<str:parent_model_name>/<int:parent_pk>/relation/<str:related_name>/',
         list.ModelList.as_view(), name='model_relation_list'),

    # path('<str:parent_name>/<int:parent_id>/<str:model_name>/list', views.ListTemplate.as_view(),
    #      name='child_model_list'),

    # path('<str:parent_name>/<str:parent_id>/<str:model_name>/action/<str:action>',
    #      views_forms.ModelActions.as_view(), name='model_action'),

    path('<str:model_name>/<str:action>/', forms.ModelActions.as_view(), name='model_action'),
    path('<str:model_name>/<str:action>/<int:pk>/', forms.ModelActions.as_view(), name='model_instance_action'),

    path('', lambda request: redirect('directory:model_list', model_name='person'), name='directory_index'),
]
