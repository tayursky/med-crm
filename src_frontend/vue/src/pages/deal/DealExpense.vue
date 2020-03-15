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
          <el-button icon="el-icon-document-add" title="Добавить" @click="addItem"/>
          <el-button icon="el-icon-refresh" title="Обновить" @click="loadModel"/>
        </div>

        <filters :filters=filters @changeFilters="changeFilters"/>
      </el-row>

      <div class="directory__total">
        <div class="directory__total__item">Всего: {{ count }}</div>
        <div class="directory__total__item">Общая сумма: {{ total }}</div>
      </div>

      <data-table :headers=headers
                  :items=items
                  :loading=loading
                  @editItem="editItem"/>

      <the-dialog :app_label=app_label
                  :model_name=model_name
                  :item=item
                  :permissions=permissions
                  @itemClose="itemClose"/>
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
        title: '',
        permissions: [],
        filters: {},
        headers: [],
        items: [],
        item: {},
        count: 0,
        total: 0,
        loading: false,
        filters_timeout: null,
      }
    },

    computed: {
      app_label() {
        let path = this.$route.fullPath.split('/');
        return path[1];
      },
      model_name() {
        let path = this.$route.fullPath.split('/');
        return path[2];
      }
    },

    mounted() {
      this.expenseInit();
    },

    watch: {
      'title'(value, fromValue) {
        document.title = value;
      },

      '$route'(toRoute, fromRoute) {
        this.expenseInit();
      },
    },

    methods: {

      expenseInit() {
        this.loadModel();
      },

      getAjaxParams: function (from = null) {
        let params = {
          'get': true,
          'from': from,
        };
        if (this.filters && this.filters.data) {
          for (let filter_key in this.filters.data) {
            params[filter_key] = JSON.stringify(this.filters.data[filter_key]);
          }
        }
        return params;
      },

      loadModel() {
        if (!this.loading) {
          this.loading = true;
          Vue.axios
            .get(this.$store.getters.root_url + this.app_label + '/' + this.model_name + '/', {params: this.getAjaxParams()})
            .then(response => {
              this.title = response.data.title;
              this.headers = response.data.headers;
              this.items = response.data.items;
              this.permissions = response.data.permissions;
              this.count = response.data.count;
              this.total = response.data.total;
              this.filters = response.data.filters;
              this.loading = false;
            })
            .catch(error => {
              console.log(error);
              this.loading = false;
            })
        }
      },

      changeFilters(key, value) {
        this.filters.data[key] = value;
        if (this.filters_timeout) {
          clearTimeout(this.filters_timeout);
        }
        this.filters_timeout = setTimeout(function () {
          this.loadModel();
        }.bind(this), 1000);
      },

      addItem() {
        this.item = {
          'id': 'add',
          'filters': this.filters
        };
      },

      editItem(item) {
        console.log('editItem:', this.item);
        this.item = item;
      },

      itemClose() {
        console.log('itemClose');
        this.item = {};
        this.loadModel();
      },

      reportExcel() {
        let params = this.getAjaxParams(null, true);
        let url = this.$store.getters.root_url + this.app_label + '/' + this.model_name + '/xls' + params;
        window.open(url, '_blank');
      },

    }
  }
</script>

<style scoped></style>
