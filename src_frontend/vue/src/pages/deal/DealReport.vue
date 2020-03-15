<template>
  <div class="directory">
    <div class="loading" v-if="loading"></div>
    <template v-else>

      <el-row class="directory__head">
        <div class="directory__title">{{ title }}</div>
        <div class="directory__buttons">
          <button type="button" class="el-button" title="Сформировать отчет" @click="reportExcel()">
            <div class="el-button__text">Exel</div>
          </button>
          <el-button icon="el-icon-refresh" title="Обновить" @click="loadModel"/>
        </div>
      </el-row>

      <filters :filters="filters" @changeFilters="changeFilters"/>

      <div v-if="summary.ordered" class="directory__total">
        <div v-for="key in summary.ordered" class="directory__total__item">
          {{ summary.labels[key] }}: {{ summary.values[key] }}
        </div>
      </div>

      <data-table :headers="headers" :items="deals" :loading="loading" @editItem="dealEdit"/>

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
        refresh: false,
        model_name: 'report',
        title: '',
        permissions: [],
        headers: [],
        deals: [],
        summary: {},
        loading: false,
        loading_timeout: null,
        filters: null,
      }
    },

    watch: {
      'refresh': function (value, fromValue) {
        if (value === true) {
          this.loadModel();
        }
      },
      'title': function (value, fromValue) {
        document.title = value;
      },
      '$route': function (toRoute, fromRoute) {
        this.reportInit();
      },
    },

    mounted() {
      this.store_subscribe = this.$store.subscribe((mutation, state) => {
        switch (mutation.type) {
          case 'set_refresh_deals':
            this.refresh = state.deal.refresh;
            break;
        }
      });
      this.reportInit();
    },
    beforeDestroy() {
      this.store_subscribe();
    },

    computed: {},

    methods: {

      reportInit() {
        this.loadModel();
      },

      filtersReset() {
        for (let key in this.filters.data) {
          this.filters.data[key] = null;
        }
      },

      getAjaxParams: function (from = null, string = false) {
        let params = {
          'from': from,
          'model_name': self.model_name,
          'get': true,
        };
        if (this.filters) {
          for (let filter_key in this.filters.data) {
            params[filter_key] = JSON.stringify(this.filters.data[filter_key]);
          }
        }
        return params;
      },

      loadModel() {
        this.loading = true;
        Vue.axios
          .get(this.$store.getters.root_url + 'deal/report/', {params: this.getAjaxParams()})
          .then(response => {
            this.title = response.data.title;
            this.headers = response.data.headers;
            this.deals = response.data.items;
            this.permissions = response.data.permissions;
            this.summary = response.data.summary;
            this.filters = response.data.filters;
          })
          .catch(error => {
            console.log(error);
          })
          .finally(() => {
            this.loading = false;
            this.$store.commit('set_refresh_deals', false);
          });
      },

      changeFilters(key, value) {
        this.filters.data[key] = value;
      },

      dealEdit(deal) {
        deal['master'] = null;
        this.$store.commit('set_deal', deal);
      },

      reportExcel() {
        let params = this.getAjaxParams(null, true);
        let url = this.$store.getters.root_url + 'deal/report/xls' + params;
        window.open(url, '_blank');
      },

    }
  }
</script>


<style scoped>

</style>
