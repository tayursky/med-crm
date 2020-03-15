<template>
  <div class="directory">
    <div class="loading" v-if="loading"></div>
    <template v-else>
      <el-row class="directory__head">
        <div class="directory__title">{{ title }}</div>
        <div class="directory__buttons">
          <el-button icon="el-icon-document-add" title="Добавить" @click="itemAdd"/>
          <el-button icon="el-icon-refresh" title="Обновить" @click="listLoad"/>
        </div>

        <filters :filters="filters" @refresh="listLoad" @changeFilters="filtersChange"/>
      </el-row>

      <div class="directory__total">
        <div class="directory__total__item">Всего: {{ count }}</div>
      </div>

      <data-table :headers="headers"
                  :items="items"
                  :loading="loading"
                  @editItem="itemEdit"/>

      <paging :paging="paging" @changePage="pageChange"/>

      <!-- Dialog form -->
      <the-dialog app_label="directory"
                  :model_name="model_name"
                  :item="item"
                  :permissions="permissions"
                  @itemClose="itemClose"/>
      <!-- End dialog form -->

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
        actions: {},
        meta_label: '',
        title: '',
        filters: {},
        headers: [],
        items: [],
        item: {},
        count: 0,
        permissions: [],
        paging: {'page': 1, 'pages': 1},
        loading: false,
        loading_timeout: null,
      }
    },

    computed: {
      model_name() {
        // TODO: разобраться с роутерами
        if (this.$route.name === 'company_mlm_agent_list') {
          return 'agent'
        }
        return this.$route.params.model_name
      }
    },
    mounted() {
      this.store_subscribe = this.$store.subscribe((mutation, state) => {
        switch (mutation.type) {
          case 'set_refresh_clients':
            this.refresh = state.client.refresh;
            break;
        }
      });
      this.listLoad();
    },
    beforeDestroy() {
      this.store_subscribe();
    },

    watch: {
      '$route'(toRoute, fromRoute) {
        // console.log('$route', toRoute.fullPath);
        this.paging.page = 1;
        this.listLoad();
      },
      'refresh'(value, fromValue) {
        if (value === true) {
          this.listLoad();
        }
      },
      'title'(value, fromValue) {
        document.title = value;
      },
    },

    methods: {
      getAjaxParams: function (from = null) {
        let params = {
          'from': from,
          'meta_label': this.meta_label,
          'model_name': this.model_name,
          'page': this.paging.page,
        };
        if (this.filters) {
          for (let _key in this.filters.data) {
            if (this.filters.data[_key]) {
              params[_key] = JSON.stringify(this.filters.data[_key]);
            }
          }
        }
        return params;
      },

      listLoad() {
        if (this.loading) return;
        this.loading = true;
        Vue.axios
          .get(this.$store.getters.root_url + 'directory/' + this.model_name + '/', {params: this.getAjaxParams()})
          .then(response => {
            this.meta_label = response.data.meta_label;
            this.title = response.data.title;
            this.filters = response.data.filters;
            this.headers = response.data.headers;
            this.actions = response.data.actions;
            this.items = response.data.items;
            this.count = response.data.count;
            this.permissions = response.data.permissions;
            this.paging = response.data.paging;
          })
          .catch(error => {
            alert(error);
          })
          .finally(() => {
            this.loading = false;
            this.$store.commit('set_refresh_clients', false);
          });
      },

      filtersChange(key, value) {
        this.filters.data[key] = value;
      },

      itemAdd() {
        if (this.meta_label === 'deal.Client') {
          this.$store.commit('set_client', {'id': 'add'});
        } else {
          this.item = {'id': 'add'};
        }
      },
      itemEdit(item) {
        if (this.actions['edit'] && this.actions['edit']['name'] === 'company_mlm_agent') {
          this.$router.push({name: this.actions['edit']['name'], params: {'agent_id': item.id}});
          return
        }
        if (this.meta_label === 'deal.Client') {
          this.$store.commit('set_client', item);
        } else {
          this.item = item;
        }
      },
      itemClose(reload = true) {
        this.item = {};
        if (reload) {
          this.listLoad();
        }
      },

      pageChange(page) {
        this.paging.page = page;
        this.listLoad();
      }

    }
  }
</script>

<style scoped></style>
