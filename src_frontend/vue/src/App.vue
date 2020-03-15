<template>
  <div class="main-wrapper">

    <div class="sidebar">
      <menu-side :menu_set="menu_set"/>
    </div>

    <div class="main-right">
      <menu-top :menu_set="menu_set"/>

      <div class="main-content">
        <transition name="flip" mode="out-in">
          <router-view></router-view>
        </transition>
      </div>
    </div>


    <client-set/>
    <deal-set/>

  </div>
</template>


<script>
  import Vue from 'vue'
  import axios from 'axios'
  import VueAxios from 'vue-axios'

  Vue.use(VueAxios, axios);

  export default {
    data() {
      return {
        menu_set: {},
        picker: new Date().toISOString().substr(0, 10),
        landscape: false,
        reactive: false,
      }
    },
    computed: {
      menu_left_() {
        for (let key in this.menu) {
          if ('url' in this.menu[key] && this.menu[key]['url'] === '/client/') {
            return this.menu[key]['subitems'];
          }
        }
      }
    },
    mounted() {
      Vue.axios.get(this.$store.getters.root_url + 'get_settings/', {})
        .then(response => {
          this.$store.commit('set_settings', response.data);
        })
        .catch(error => {
          console.log(error);
        });
      Vue.axios.get(this.$store.getters.root_url + 'get_routes/', {})
        .then(response => {
          this.menu_set = response.data;
        })
        .catch(error => {
          console.log(error);
        });
    },
    methods: {}
  }
</script>


<style></style>
