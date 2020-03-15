import VueRouter from 'vue-router'
import PageLogin from './pages/Login'

import DealMonth from './pages/deal/DealMonth'
import DealSchedule from './pages/deal/DealSchedule'
import DealDay from './pages/deal/DealDay'
import DealTasks from './pages/deal/DealTasks'
import DealExpense from './pages/deal/DealExpense'
import DealReport from './pages/deal/DealReport'
import DealOnline from './pages/deal/Online'

import DealKanban from './pages/deal/DealKanban'
import DealList from './pages/deal/DealList'

import WorkingCalendar from './pages/directory/WorkingCalendar'
import PageDirectory from './pages/Directory'
import CompanyGroupList from './pages/company/GroupList'
import CompanyGroup from './pages/company/Group'
import CompanyUserList from './pages/company/UserList'
import CompanyUserReward from './pages/company/UserReward'
import CompanyUser from './pages/company/User'
import CompanyTimeTable from './pages/company/TimeTable'
import MlmAgent from './pages/company/MlmAgent'
import MlmManager from './pages/company/MlmManager'

import PageSettings from './pages/Settings'


export default new VueRouter({
  routes: [
    // {
    // 	name: 'login', path: '/login', component: PageLogin
    // }, {
    // 	name: 'logout', path: '/login', component: PageLogin
    //  }, {
    //   name: 'deal_online', component: DealOnline, path: '/deal/online/'
    // },
    {
      name: 'deal_month', component: DealMonth, path: '/deal/month/'
    }, {
      name: 'deal_schedule', component: DealSchedule, path: '/deal/schedule/'
    }, {
      //   name: 'deal_day', component: DealDay, path: '/deal/day/'
      // }, {
      name: 'deal_kanban', component: DealKanban, path: '/deal/kanban/'
    }, {
      name: 'deal_list', component: DealList, path: '/deal/list/'
    }, {
      name: 'deal_task_list', component: DealTasks, path: '/deal/task/'
    }, {
      name: 'deal_expense', component: DealExpense, path: '/deal/dealexpense/'
    }, {
      name: 'deal_report', component: DealReport, path: '/deal/report/'
    }, {
      name: 'deal_client', component: PageDirectory, path: '/deal/:model_name/',
    },
    // Company
    {
      name: 'company_user', component: CompanyUser, path: '/company/user/:user_id/'
    }, {
      name: 'company_user_list', component: CompanyUserList, path: '/company/user/'
    }, {
      name: 'company_user_reward', component: CompanyUserReward, path: '/company/user_reward/'
    }, {
      name: 'company_group', component: CompanyGroup, path: '/company/group/:group_id/'
    }, {
      name: 'company_group_list', component: CompanyGroupList, path: '/company/group/'
    }, {
      name: 'company_timetable', component: CompanyTimeTable, path: '/company/timetable/'
    }, {
      name: 'company_expense', component: DealExpense, path: '/company/expense/'
    }, {
      name: 'company_mlm_agent', component: MlmAgent, path: '/company/mlm_agent/:agent_id'
    }, {
      name: 'mlm_cabinet_manager', component: MlmManager, path: '/company/mlm_cabinet_manager/'
    }, {
      name: 'company_mlm_agent_list', component: PageDirectory, path: '/company/mlm_agent/',
      params: {model_name: 'agent', meta_label: 'agent'}
    }, {
      name: 'company_department', component: PageDirectory, path: '/company/:model_name/'
    }, {
      name: 'company_eventlog', component: PageDirectory, path: '/company/:model_name/'
    },
    // Settings
    {
      name: 'settings', component: PageSettings, path: '/settings/'
    },
    // Directory
    {
      name: 'working_calendar', component: WorkingCalendar, path: '/directory/working_calendar/',
    }, {
      name: 'directory_list', component: PageDirectory, path: '/directory/:model_name/',
    },
  ],
  mode: 'history'
})
