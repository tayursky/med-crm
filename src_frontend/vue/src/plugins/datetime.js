// import UserContainer from './UserContainer'

const Plugin = {
  install(Vue, options) {
    // <g-user-container> component will be globally available
    // Vue.component('GUserContainer', UserContainer);

    Vue.mixin({
      computed: {
        // `users` will be available globally
        users() {
          return this.$store.getters.users
        },
      }
    });

    // $sayHello is available within components
    Vue.prototype.$sayHello = function (name) {
      return `Hello ${name}!`
    }
  }
};

