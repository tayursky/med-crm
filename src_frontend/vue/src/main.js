import Vue from 'vue'

import VueRouter from 'vue-router'
import router from './routes'
import store from './store'

Vue.use(VueRouter);

import ElementUI from 'element-ui';
import locale from 'element-ui/lib/locale/lang/ru-RU'

Vue.use(ElementUI, {locale});

import {Drag, Drop} from 'vue-drag-drop';

Vue.component('drag', Drag);
Vue.component('drop', Drop);

import MaskedInput from 'vue-masked-input'

Vue.component('MaskedInput', MaskedInput);

import App from './App.vue'
import DataTable from './components/DataTable'
import TheDialog from './components/TheDialog'
import TheForm from './components/TheForm'
import Filters from './components/Filters'
import FormField from './components/FormField'
import MenuSide from './components/MenuSide'
import MenuTop from './components/MenuTop'
import Paging from './components/Paging'
import SipCall from './components/SipCall'
import SipGet from './components/SipGet'

import ClientSet from './pages/deal/tabs/ClientSet'
import DealSet from './pages/deal/tabs/DealSet'
import DealForm from './pages/deal/tabs/DealForm'
import TabComments from './pages/deal/tabs/TabComments'
import TabHistory from './pages/deal/tabs/TabHistory'
import TabTasks from './pages/deal/tabs/TabTasks'
import TabSms from './pages/deal/tabs/TabSms'
import DealFormTask from './pages/deal/DealFormTask'

Vue.component('DataTable', DataTable);
Vue.component('TheDialog', TheDialog);
Vue.component('TheForm', TheForm);
Vue.component('Filters', Filters);
Vue.component('FormField', FormField);
Vue.component('MenuSide', MenuSide);
Vue.component('MenuTop', MenuTop);
Vue.component('Paging', Paging);
Vue.component('SipCall', SipCall);
Vue.component('SipGet', SipGet);

Vue.component('ClientSet', ClientSet);
Vue.component('DealSet', DealSet);
Vue.component('TabComments', TabComments);
Vue.component('TabHistory', TabHistory);
Vue.component('TabSms', TabSms);
Vue.component('TabTasks', TabTasks);
Vue.component('DealForm', DealForm);
Vue.component('DealFormTask', DealFormTask);

// import '../../stylus/element-ui-2.13.0.css';
import '../../stylus/index.styl';


import moment from 'moment';
Vue.prototype.$moment = moment;

new Vue({
  el: '#app',
  render: h => h(App),
  router,
  store
});
