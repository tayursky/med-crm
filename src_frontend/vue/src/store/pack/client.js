export default {
  state: {
    refresh: false,
    item: {id: null},
  },

  getters: {

  },

  mutations: {
    set_client(state, item) {
      state.item = item;
    },
    set_refresh_clients(state, value) {
      state.refresh = value;
    },

  },

  actions: {}

}

