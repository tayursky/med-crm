import Vue from 'vue'
import Vuex from 'vuex'

import client from './pack/client'
import deal from './pack/deal'

Vue.use(Vuex);

export default new Vuex.Store({
  modules: {
    deal, client
  }
})
