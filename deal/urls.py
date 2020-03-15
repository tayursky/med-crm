# from periods.period import TimeInterval as Period
from django.urls import path
from django.shortcuts import redirect
from deal.views.client import ClientListView
from deal.views.branch import BranchList
from deal.views.deal import DealFormView, DealCostView
from deal.views.paper import DealPaperView, DealDocView
from deal.views.deal_history import DealHistoryListView
from deal.views.kanban import ServiceList, DealKanbanView
from deal.views.deal_list import DealListView
from deal.views.deal_month import MonthView
from deal.views.schedule import ScheduleView, ScheduleXlsView
from deal.views.deal_comment import DealCommentListView
from deal.views.deal_task import DealTaskListView
from deal.views.expense import ExpenseListView
from deal.views.report import ReportListView
from deal.views.online import OnlineView

from directory.views import forms, list

urlpatterns = [
    path('get_branch_list/', BranchList.as_view(), name='branch_list'),
    path('get_service_list/', ServiceList.as_view(), name='deal_service_list'),
    path('online/', OnlineView.as_view(), name='deal_online'),

    path('paper/', DealPaperView.as_view(), name='deal_paper'),
    path('doc/', DealDocView.as_view(), name='deal_doc'),

    path('month/', MonthView.as_view(), name='deal_month'),
    path('schedule/xls/', ScheduleXlsView.as_view(), name='deal_schedule_xls'),
    path('schedule/', ScheduleView.as_view(), name='schedule'),
    # path('day/<str:action>/', DayView.as_view(), name='deal_day_action'),
    # path('day/', DayView.as_view(), name='deal_day'),

    path('kanban/', DealKanbanView.as_view(), name='deal_kanban'),
    path('list/', DealListView.as_view(), name='deal_list'),

    path('comment/', DealCommentListView.as_view(), name='deal_comment_list'),
    path('history/', DealHistoryListView.as_view(), name='deal_history_list'),

    path('dealexpense/', ExpenseListView.as_view(), name='deal_expense_list',
         kwargs=dict(model_name='dealexpense')),
    path('dealexpense/xls/', ExpenseListView.as_view(), name='deal_expense_xls',
         kwargs=dict(model_name='dealexpense', action='get_xls')),
    path('dealexpense/<str:action>/', forms.ModelActions.as_view(), name='deal_expense_action',
         kwargs=dict(model_name='dealexpense')),
    path('dealexpense/<str:action>/<int:pk>/', forms.ModelActions.as_view(), name='deal_expense_action',
         kwargs=dict(model_name='dealexpense')),

    path('report/', ReportListView.as_view(), name='deal_report_list'),
    path('report/xls/', ReportListView.as_view(), name='deal_report_xls',
         kwargs=dict(action='get_xls', model_name='deal')),
    path('report/<str:action>/', forms.ModelActions.as_view(), name='deal_report_action',
         kwargs=dict(model_name='deal')),
    path('report/<str:action>/<int:pk>/', forms.ModelActions.as_view(), name='deal_report_action',
         kwargs=dict(model_name='deal')),

    path('client/', list.ModelList.as_view(), name='client_list',
         kwargs=dict(model_name='client')),
    path('client/<int:pk>/', list.ModelDetail.as_view(), name='client_view',
         kwargs=dict(model_name='client')),
    path('client/<str:action>/', forms.ModelActions.as_view(), name='client_action',
         kwargs=dict(model_name='client')),
    path('client/<str:action>/<int:pk>/', forms.ModelActions.as_view(), name='client_instance_action',
         kwargs=dict(model_name='client')),

    path('task/', DealTaskListView.as_view(), name='deal_task_list'),
    # path('task/<str:action>/', DealTaskView.as_view(), name='deal_task'),
    # path('task/<str:action>/<str:task>/', DealTaskView.as_view(), name='deal_task_instance'),

    path('cost/', DealCostView.as_view(), name='deal_cost'),
    path('<str:action>/', DealFormView.as_view(), name='deal'),
    path('<str:action>/<str:pk>/', DealFormView.as_view(), name='deal_instance'),

    # path('<str:parent_name>/<int:parent_id>/<str:model_name>/list', views.ListTemplate.as_view(),
    #      name='child_model_list'),

    # path('<str:parent_name>/<str:parent_id>/<str:model_name>/action/<str:action>',
    #      views_forms.ModelActions.as_view(), name='model_action'),

]
