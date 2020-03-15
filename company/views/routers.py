from deal.models import Expense
from directory.utils import get_menu_items
from company.models import Department, EventLog
from mlm.models import Agent

COMPANY_ITEMS = get_menu_items([
    dict(
        name='company',
        label='Компания',
        url='/company',
        icon='book',
        subitems=[
            dict(
                label=u'Сотрудники', router_name='company_user_list', url='/company/user',
                perm='company.view_user', subitems_list=['company_user'], icon='el-icon-user'
            ),
            dict(
                label=u'Табель', router_name='company_timetable', url='/company/timetable',
                icon='el-icon-date', perm='company.view_timetable'
            ),
            dict(
                label=u'Отчет: вознаграждения сотрудников', router_name='company_user_reward',
                url='/company/user_reward', perm='company.reward_user', icon='el-icon-data-analysis'
            ),
            dict(
                model=Department, router_name='company_department', url='/company/department',
                split=True, perm='company.view_department'
            ),
            dict(
                model=Expense, router_name='company_expense', url='/company/expense',
                perm='deal.view_expense'
            ),
            dict(
                label=u'Группы доступа', router_name='company_group_list', url='/company/group',
                perm='company.view_usergroup', subitems_list=['company_group'], icon='el-icon-bank-card'
            ),
            dict(
                model=EventLog, router_name='company_eventlog', url='/company/eventlog',
                perm='company.view_eventlog', subitems_list=['company_eventlog']
            ),
            dict(
                model=Agent, router_name='company_mlm_agent_list', url='/company/mlm_agent',
                split=True, perm='mlm.view_agent', subitems_list=['company_mlm_agent'], icon='el-icon-bank-card'
            ),
            dict(
                label=u'Кабинет менеджера', router_name='mlm_cabinet_manager',
                url='/company/mlm_cabinet_manager', perm='mlm.mlm_manager',
                subitems_list=['mlm_cabinet_manager'], icon='el-icon-user'
            ),

            # dict(split=True),
        ]
    ),

])
