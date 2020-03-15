<template>
  <div class="directory user_reward">

    <div class="loading" v-if="loading"></div>
    <template v-else>

      <el-row class="directory__head">
        <div class="directory__title">{{ title }}</div>

        <div class="directory__buttons">
          <el-button icon="el-icon-refresh" title="Обновить" @click="rewardload"/>
        </div>

        <filters :filters=filters @changeFilters="changeFilters"/>
      </el-row>

      <div v-if="reward_set.items" class="directory__total">
        <div class="directory__total__item">Всего: {{ reward_set.items.length }}</div>
      </div>

      <table v-if="reward_set.items" class="user_reward__table">
        <tbody>
        <tr v-for="item in reward_set.items" class="user_reward__table__tr">
          <td class="user_reward__table__td">
            {{ item.user}}
          </td>
          <td class="user_reward__table__td">
            <div v-for="(service, service_id) in item.services">
              {{ services[service_id] }}: {{ service }}
            </div>
          </td>
          <td class="user_reward__table__td">
            {{ item.reward }}
          </td>
        </tr>
        </tbody>
      </table>

    </template>

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
        loading: false,
        title: '',
        permissions: [],
        reward_set: {},
        masters: {},
        services: {},
        filters_timeout: null,
        filters: {},
      }
    },

    mounted() {
      this.rewardload();
    },

    watch: {
      'title'(value, fromValue) {
        document.title = value;
      },
      '$route'(toRoute, fromRoute) {
        this.rewardload();
      },
    },

    methods: {

      getAjaxParams: function () {
        let params = {'get': true};
        if (this.filters && this.filters.data) {
          for (let filter_key in this.filters.data) {
            if (this.filters.data[filter_key]) {
              params[filter_key] = JSON.stringify(this.filters.data[filter_key]);
            }
          }
        }
        return params;
      },

      rewardload() {
        if (this.loading) return;
        this.loading = true;
        Vue.axios
          .get(this.$store.getters.root_url + 'company/user_reward/', {params: this.getAjaxParams()})
          .then(response => {
            this.title = response.data.title;
            this.filters = response.data.filters;
            this.reward_set = response.data.reward_set;
            this.services = response.data.services;
            this.permissions = response.data.permissions;
          })
          .catch(error => {
            console.log(error);
          })
          .finally(() => {
            this.loading = false;
          });
      },

      changeFilters(key, value) {
        this.filters.data[key] = value;
        // if (this.filters_timeout) {
        //   clearTimeout(this.filters_timeout);
        // }
        // this.filters_timeout = setTimeout(function () {
        //   this.rewardload();
        // }.bind(this), 1000);
      },

    }
  }
</script>

<style scoped></style>
