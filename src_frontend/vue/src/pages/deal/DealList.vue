<template>
  <div class="deal-content">
    <div v-if="loading" class="loading"></div>
    <div v-else class="i-day deal-list">
      <el-row class="directory__head">
        <div class="directory__title">{{ title }}</div>
        <div class="directory__buttons">
          <el-button icon="el-icon-close" title="Сбросить" @click="filterReset"/>
          <el-button icon="el-icon-refresh-right" title="Обновить" @click="listRefresh"/>
        </div>
      </el-row>

      <filters :filters="filters" @refresh="listRefresh" @changeFilters="filtersChange"/>

      <div v-if="count" class="directory__total">
        <div class="directory__total__item">{{ count }}</div>
      </div>

      <table class="deal-list__list deal-list__list">
        <tbody>
        <tr v-for="(deal, deal_index) in deals" class="deal-list__item" @click="dealEdit(deal)">
          <td class="deal-list__item__title"
              :style="{backgroundColor: stages[deal.step].background_color, color: stages[deal.step].color}">
            {{ deal.title }}
          </td>
          <td class="deal-list__item__minutes" :class="'pravka_'+deal.pravka">{{ deal.minutes }}</td>
          <td class="deal-list__persons">
            <div v-for="person in deal.persons" class="deal-list__persons__item">{{ person.string }}</div>
          </td>
        </tr>
        </tbody>
      </table>
    </div>

    <paging :paging="paging" @changePage="pageChange"/>

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
        title: '',
        loading: true,
        filters: null,
        stages: [],
        deals: [],
        count: 0,
        paging: {'page': 1, 'pages': 1},
      }
    },
    watch: {
      'refresh': function (value, fromValue) {
        if (value === true) {
          this.listRefresh();
        }
      },
      'title': function (value, fromValue) {
        document.title = value;
      }
    },
    computed: {},
    created() {
    },
    mounted() {
      this.store_subscribe = this.$store.subscribe((mutation, state) => {
        switch (mutation.type) {
          case 'set_refresh_deals':
            this.refresh = state.deal.refresh;
            break;
        }
      });
      this.paging.page = 1;
      this.listRefresh();
    },
    beforeDestroy() {
      this.store_subscribe();
    },

    methods: {

      listRefresh(get_day) {
        this.loading = true;
        let params = {
          'get': true,
          'page': this.paging.page,
        };
        if (this.filters) {
          for (let filter_key in this.filters.data) {
            params[filter_key] = JSON.stringify(this.filters.data[filter_key]);
          }
        }
        params['branch'] = this.$store.state.deal.branch.id;
        Vue.axios
          .get(this.$store.getters.root_url + 'deal/list/', {params: params})
          .then(response => {
            this.title = response.data.title;
            this.filters = response.data.filters;
            this.stages = response.data.stages;
            this.deals = response.data.deals;
            this.paging = response.data.paging;
            this.count = response.data.count;
          })
          .catch(error => {
            console.log(error);
          })
          .finally(() => {
            this.loading = false;
            this.$store.commit('set_refresh_deals', false);
          });
      },

      dealEdit(deal) {
        this.$store.commit('set_deal', deal);
      },

      filtersChange(key, value) {
        this.filters.data[key] = value;
        if (key === 'branch') {
          this.$store.commit('set_branch', {'id': value});
        }
      },

      filterReset() {
        for (let key in this.filters.data) {
          console.log(key);
          this.filters.data[key] = '';
        }
        this.listRefresh();
      },

      pageChange(page) {
        this.paging.page = page;
        this.listRefresh();
      }

    }
  }
</script>


<style scoped>

</style>
