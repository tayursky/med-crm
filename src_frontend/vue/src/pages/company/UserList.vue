<template>
  <div class="directory">
    <div class="loading" v-if="loading"></div>

    <template v-else>

      <el-row class="directory__head">
        <div class="directory__title">{{ title }}</div>

        <div class="directory__buttons">
          <el-button icon="el-icon-document-add" @click="editItem({'id': 'add'})"></el-button>
          <el-button icon="el-icon-refresh" @click="loadModel"></el-button>
        </div>

        <filters :filters="filters" @changeFilters="changeFilters"></filters>

      </el-row>

      <div>Всего: {{ count }}</div>

      <data-table
          :headers="headers"
          :items="items"
          :loading="loading"
          @editItem="editItem">
      </data-table>

      <paging :paging="paging" @changePage="changePage"></paging>

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
        filters: {},
        headers: [],
        items: [],
        count: 0,
        paging: {'page': 1, 'pages': 1},
        loading: false,
        loading_timeout: null
      }
    },

    computed: {
      model_name() {
        return this.$route.params.model_name
      }
    },

    mounted() {
      this.directoryInit();
    },

    watch: {
      'title'(value, fromValue) {
        document.title = value;
      },
      '$route'(toRoute, fromRoute) {
        this.directoryInit();
      },
    },

    methods: {
      directoryInit() {
        this.paging.page = 1;
        this.loadModel();
      },

      getAjaxParams: function (from = null) {
        var params = {
          'from': from,
          'model_name': this.model_name,
          'page': this.paging.page,
        };
        if (this.filters) {
          for (let filter_key in this.filters.data) {
            params[filter_key] = this.filters.data[filter_key];
          }
        }
        return params;
      },

      loadModel() {
        if (!this.loading) {
          this.loading = true;
          Vue.axios.get(this.$store.getters.root_url + 'company/user/', {params: this.getAjaxParams()})
            .then(response => {
              this.title = response.data.title;
              this.headers = response.data.headers;
              this.items = response.data.items;
              this.count = response.data.count;
              this.paging = response.data.paging;
              this.filters = response.data.filters;
              this.loading = false;
            })
            .catch(error => {
              console.log(error);
              this.loading = false;
            })
        }
      },

      changeFilters: function (key, value) {
        this.paging.page = 1;
        this.filters.data[key] = value;
        if (this.loading_timeout) {
          clearTimeout(this.loading_timeout);
        }
        this.loading_timeout = setTimeout(function () {
          this.loadModel();
        }.bind(this), 1000);
      },

      addItem() {
        this.item = {'id': 'add'};
      },

      changePage(page) {
        this.paging.page = page;
        this.loadModel();
      },

      editItem(item) {
        console.log('editItem', item);
        this.$router.push({name: 'company_user', params: {'user_id': item.id}})
      }

    }
  }
</script>

<style scoped>
</style>
