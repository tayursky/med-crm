export default {
  state: {
    current_day: null,
    refresh: false,
    item: {id: null},
    drag_drop: {id: null, title: null},
    branch: {'id': null},
    service: {'id': null},
    settings: {},
    permissions: [],
  },

  getters: {
    root_url() {
      const protocol = document.location.protocol;
      const host = document.location.host;
      if (host === 'localhost:8080') {
        return 'http://127.0.0.1:8000/';
      } else if (host === 'localhost:8081') {
        return 'http://127.0.0.1:8001/';
      }
      return protocol + '//' + host + '/';
    }
  },

  mutations: {
    set_current_day(state, value) {
      state.current_day = value;
    },

    set_branch(state, value) {
      console.log('set_branch', value);
      state.branch = value;
    },

    set_service_id(state, value) {
      state.service.id = value;
    },

    set_settings(state, data) {
      state.settings = data.settings;
      state.permissions = data.permissions;
    },

    set_deal(state, item) {
      state.item = item;
    },

    set_refresh_deals(state, value) {
      state.refresh = value;
    },

    set_drag_drop(state, data) {
      state.drag_drop = {
        'id': data.id ? data.id : null,
        'title': data.title ? data.title : null,
        'start_iso': data.start_iso ? data.start_iso : null,
        'end_iso': data.end_iso ? data.end_iso : null,
        'minutes': data.minutes ? data.minutes : null,
        'master': data.master && data.master.id ? data.master.id : null,
      };
    },

    update_drag_drop(state, data) {
      state.drag_drop.drop = (typeof data['drop'] !== 'undefined');
      if (typeof data['id'] !== 'undefined') state.drag_drop.id = data.id;
      if (typeof data['title'] !== 'undefined') state.drag_drop.title = data.title;
      if (typeof data['start_iso'] !== 'undefined') state.drag_drop.start_iso = data.start_iso;
      if (typeof data['end_iso'] !== 'undefined') state.drag_drop.end_iso = data.end_iso;
      if (typeof data['minutes'] !== 'undefined') state.drag_drop.minutes = data.minutes;
      if (typeof data['master'] !== 'undefined') state.drag_drop.master = data.master.id;
    },
  },

  actions: {}

}

