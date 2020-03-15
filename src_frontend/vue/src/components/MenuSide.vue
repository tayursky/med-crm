<template>
  <div>

    <a href="/" class="sidebar__logo">
      <div class="sidebar__logo__text">CRM:ПРАВКА</div>
    </a>

    <div class="sidebar__router">
      <template v-for="(item, item_key) in menu_left">

        <hr v-if="'split' in item" class="sidebar__router__split">

        <router-link v-if="'router_name' in item && 'params' in item"
                     tag="a"
                     class="sidebar__router__item"
                     :key="item_key"
                     :to="{name: item.router_name, params: item.params}"
                     active-class="is_active"
                     exact>
          <i v-if="item.icon" :class="item.icon"></i>
          <div class="sidebar__router__label">{{ item.label }}</div>
        </router-link>

        <router-link v-else-if="'router_name' in item"
                     tag="a"
                     class="sidebar__router__item"
                     :key="item_key"
                     :to="{name: item.router_name}"
                     active-class="is_active"
                     exact>
          <i v-if="item.icon" :class="item.icon"></i>
          <div class="sidebar__router__label">{{ item.label }}</div>
        </router-link>

        <a v-else-if="'url' in item"
           class="sidebar__router__item"
           :href="getUrl(item)">
          <i v-if="item.icon" :class="item.icon"></i>
          <div class="sidebar__router__label">{{ item.label }}</div>
        </a>

      </template>
    </div>

  </div>
</template>


<script>
  import Vue from 'vue'
  import axios from 'axios'
  import VueAxios from 'vue-axios'

  Vue.use(VueAxios, axios);

  export default {
    props: ['menu_set'],
    data() {
      return {
        activeIndex: '0',
      }
    },
    watch: {
      menu_set: function (val, oldVal) {
        // console.log('watch menu_left', val);
      },

      // '$route'(value, fromRoute) {
      //   console.log('watch $route, ' + value.name);
      //   // console.log(value);
      //   this.menu_left = this.getMenuLeft(value.name);
      // }
    },

    computed: {
      menu_left() {
        // console.log('menu_left, menu_set');
        // console.log(this.menu_set);
        for (let key in this.menu_set.top) {
          // console.log('this.menu_set.top[key]');
          // console.log(this.menu_set.top[key]);
          let item = this.menu_set.top[key];
          // console.log(this.$route.name);
          // console.log(item.subitems_list);
          if (item.subitems_list && item.subitems_list.indexOf(this.$route.name) !== -1) {
            // console.log(this.$route.name);
            // console.log(item.subitems_list);
            return item.subitems;
          }
        }
        return [];
      },
    },

    mounted() {
      // console.log('mount', this.$route.name);
    },

    methods: {
      getUrl(item) {
        let url = item.url + '';
        for (let param_key in this.$route.params) {
          url = url.replace(':' + param_key, this.$route.params[param_key]);
          // console.log(url, ':' + param_key, this.$route.params[param_key]);
        }
        return url;
      },

      getMenuLeft(route_name) {

        // for (let key in this.menu_set['dynamic']) {
        // 	let item = this.menu_set['dynamic'][key];
        // 	if (item.routers.indexOf(route_name) !== -1) {
        // 		return item.items;
        // 	}
        // }

        for (let key in this.menu_set.top) {
          let item = this.menu_set.top[key];

          if (item.subitems_list && item.subitems_list.indexOf(route_name) !== -1) {
            console.log(item.subitems);
            return item.subitems;
          }
        }

      }
    }
  }
</script>


<style>
</style>
