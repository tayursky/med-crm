from directory.utils import get_menu_items
from deal.models import *

DEAL_ITEMS = get_menu_items([
    dict(
        name='deal',
        label='Сделки',
        url='/deal',
        icon='el-icon-tickets',
        subitems=[
            dict(
                label=u'Месяц', router_name='deal_month', perm='deal.view_deal', url='/deal/month/',
                icon='el-icon-date'
            ),
            dict(
                label=u'Расписание', router_name='deal_schedule', perm='deal.view_deal', url='/deal/schedule/',
                icon='el-icon-date'
            ),
            # dict(
            #     label=u'День', router_name='deal_day', perm='deal.view_deal', url='/deal/day/',
            #     icon='el-icon-date'
            # ),
            dict(
                label=u'Канбан', router_name='deal_kanban', perm='deal.view_deal', url='/deal/kanban/',
                split=True, icon='el-icon-data-board'
            ),
            dict(
                label=u'Список сделок', router_name='deal_list', perm='deal.view_deal', url='/deal/list/',
                icon='el-icon-tickets'
            ),
            dict(
                model=Client, router_name='deal_client', perm='deal.view_client', url='/deal/client/'
            ),
            dict(
                label=u'Задачи', router_name='deal_task_list', perm='deal.view_dealtask', url='/deal/task/',
                split=True, icon='el-icon-s-order'
            ),
            dict(
                label=u'Отчеты', router_name='deal_report', perm='deal.view_deal', url='/deal/report/',
                split=True, icon='el-icon-data-analysis'
            ),
            dict(
                label=u'Расходы', router_name='deal_expense', perm='deal.view_dealexpense', url='/deal/dealexpense/',
                icon='el-icon-pie-chart'
            ),
            # dict(
            #     label=u'Онлайн запись', router_name='deal_online', perm='deal.add_deal', url='/deal/online/',
            #     split=True, icon='el-icon-position'
            # ),
        ]
    ),
])
