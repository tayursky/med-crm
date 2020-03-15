# from periods.period import TimeInterval as Period
from django.urls import path
from django.shortcuts import redirect

from company.views.timegroup import TimeGroupView
from company.views.timetable import TimeTableList, TimeTableSet, TimeTableShift
from company.views.user import UserListView, UserView
from company.views.user_reward import UserReward
from company.views.user_group import GroupListView, GroupView
from deal.views.expense import ExpenseListView
from directory.views import forms, list, remote_search
from mlm.views.mlm_agent import MLMAgentView, MLMChildAgentView, MLMChildAgentTotalView
from mlm.views.mlm_manager import MLMCabinetManagerView, MLMCabinetManagerInviteView, MLMCabinetManagerPaymentsView, \
    MLMCabinetManagerCreateAgentView

urlpatterns = [
    path('department/', list.ModelList.as_view(), name='department_list',
         kwargs=dict(model_name='department')),
    path('department/<int:pk>/', list.ModelDetail.as_view(), name='department_view',
         kwargs=dict(model_name='department')),
    path('department/<str:action>/', forms.ModelActions.as_view(), name='department_action',
         kwargs=dict(model_name='department')),
    path('department/<str:action>/<int:pk>/', forms.ModelActions.as_view(), name='department_instance_action',
         kwargs=dict(model_name='department')),

    path('timetable/', TimeTableList.as_view(), name='company_timetable'),
    path('timetable/set/<str:action>/', TimeTableSet.as_view(), name='company_timetable_set'),
    path('timetable/<str:action>/', TimeTableShift.as_view(), name='company_timetable_action'),
    path('timetable/<str:action>/<int:pk>/', TimeTableShift.as_view(), name='company_timetable_shift'),

    path('timegroup/<str:action>/', TimeGroupView.as_view(), name='company_timegroup_action'),
    path('timegroup/<str:action>/<int:pk>/', TimeGroupView.as_view(), name='company_timegroup_shift'),

    path('expense/', ExpenseListView.as_view(), name='company_expense_list',
         kwargs=dict(model_name='expense')),
    path('expense/xls/', ExpenseListView.as_view(), name='company_expense_xls',
         kwargs=dict(model_name='expense', action='get_xls')),
    path('expense/<str:action>/', forms.ModelActions.as_view(), name='company_expense_action',
         kwargs=dict(model_name='expense')),
    path('expense/<str:action>/<int:pk>/', forms.ModelActions.as_view(), name='company_expense_action',
         kwargs=dict(model_name='expense')),

    path('user/', UserListView.as_view(), name='user_list'),
    path('user/<str:pk>/', UserView.as_view(), name='user_view'),
    path('user/<str:pk>/<str:action>/', UserView.as_view(), name='user_action'),

    path('user_reward/', UserReward.as_view(), name='company_user_reward'),

    path('group/', GroupListView.as_view(), name='group_list'),
    path('group/<str:pk>/', GroupView.as_view(), name='group_view'),
    path('group/<str:pk>/<str:action>/', GroupView.as_view(), name='group_action'),

    path('mlm_agent/', list.ModelList.as_view(), kwargs=dict(model_name='agent'), name='mlm_agent_list'),
    path('mlm_agent/<str:pk>/', MLMAgentView.as_view(), name='mlm_agent'),
    path('mlm_agent/<str:pk>/child_agents/', MLMChildAgentView.as_view(), name='mlm_child_agents'),
    path('mlm_agent/<str:pk>/child_agents_total/', MLMChildAgentTotalView.as_view(), name='mlm_child_agents_total'),

    path('mlm_cabinet_manager/', MLMCabinetManagerView.as_view(), name='mlm_cabinet_manager',
         kwargs=dict(model_name='agent')),
    path('mlm_cabinet_manager/invite/', MLMCabinetManagerInviteView.as_view(), name='mlm_cabinet_manager_invite'),
    path('mlm_cabinet_manager/payments/', MLMCabinetManagerPaymentsView.as_view(), name='mlm_cabinet_manager_payments'),
    path('mlm_cabinet_manager/<str:action>/', MLMCabinetManagerCreateAgentView.as_view(),
         name='mlm_cabinet_manager_create_agent'),

]
