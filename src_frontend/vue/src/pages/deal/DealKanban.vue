<template>
  <div class="deal-content kanban">
    <div v-if="loading" class="loading"></div>
    <div v-else>
      <el-row class="directory__head">
        <div class="directory__title">{{ title }}</div>
        <div class="directory__buttons">
          <el-button icon="el-icon-close" title="Сбросить" @click="filtersReset"/>
          <el-button icon="el-icon-refresh-right" title="Обновить" @click="listRefresh"/>
        </div>
      </el-row>

      <filters :filters="filters" @changeFilters="filtersChange"/>

      <div class="kanban__table">
        <div v-for="(stage, stage_index) in stages" class="kanban__stage" :style="{width: stage_width}">
          <div class="kanban__stage__mount">{{ deals[stage.step-1].total }} руб.</div>
          <div class="kanban__stage__head" :style="{color: stage.color, backgroundColor: stage.background_color}">
            {{ stage.label }}
            <span style="float: right">{{ deals[stage.step-1].client_count }}</span>
          </div>

          <!-- Deals -->
          <div v-for="(deal, deal_index) in deals[stage.step-1].items"
               class="kanban__deal"
               :style="{borderColor: stages[stage.step-1].background_color}"
               @click="dealEdit(deal)">
            <div class="kanban__deal__title">
              <div class="kanban__deal__date">{{ deal.id }} | {{ deal.start_string }}</div>
              <div v-if="deal.minutes" class="kanban__deal__minutes">{{ deal.minutes }}</div>
              <div class="kanban__deal__persons_count" :class="'pravka_'+deal.pravka">
                {{ deal.persons.length }}
              </div>
            </div>
            <div class="clearfix"></div>
            <div v-if="deal.arrear || deal.comment" class="kanban__deal__comment">
              <div v-if="deal.comment" class="kanban__deal__comment__text">{{ deal.comment }}</div>
            </div>
            <div class="clearfix"></div>
            <div class="kanban__deal__persons">
              <div v-for="person in deal.persons" class="kanban__deal__person">
                <span v-if="person.control">К: </span><span v-else>П: </span>{{ person.cache.full_name }}
                <span v-if="person.cache.age">({{ person.cache.age }})</span>{{ person.cache.phone }}
              </div>
            </div>
            <div class="clearfix"></div>
          </div>
        </div>
        <!-- End deals -->

      </div>
    </div>
  </div>

</template>


<script>
  import Vue from 'vue'
  import axios from 'axios'
  import VueAxios from 'vue-axios'
  import Kanban_deal from "./tabs/DealForm";

  Vue.use(VueAxios, axios);

  export default {
    components: {Kanban_deal},
    data() {
      return {
        refresh: false,
        title: '',
        loading: true,
        filters_timeout: null,
        filters: null,
        stages: [],
        deals: {},
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
      },
    },
    computed: {
      stage_width() {
        return 100 / this.stages.length + '%'
      }
    },
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
      this.listRefresh();
    },
    beforeDestroy() {
      this.store_subscribe();
    },

    methods: {

      listRefresh() {
        this.loading = true;
        let params = {
          'get': true,
        };
        if (this.filters) {
          for (let filter_key in this.filters.data) {
            params[filter_key] = JSON.stringify(this.filters.data[filter_key]);
          }
        }
        params['branch'] = this.$store.state.deal.branch.id;
        if (!params['service']) {
          params['service'] = this.$store.state.deal.service.id;
        }
        Vue.axios
          .get(this.$store.getters.root_url + 'deal/kanban/', {params: params})
          .then(response => {
            this.title = response.data.title;
            this.filters = response.data.filters;
            this.stages = response.data.stages;
            this.deals = response.data.deals;
          })
          .catch(error => {
            console.log(error);
          })
          .finally(() => {
            this.loading = false;
            this.$store.commit('set_refresh_deals', false);
          });
        // console.log(this.deal);
      },

      dealEdit(deal) {
        this.$store.commit('set_deal', deal);
      },

      filtersChange(key, value) {
        this.filters.data[key] = value;
        if (key === 'branch') {
          this.$store.commit('set_branch', {'id': value});
        }
        if (this.filters_timeout) {
          clearTimeout(this.filters_timeout);
        }
        this.filters_timeout = setTimeout(function () {
          this.listRefresh();
        }.bind(this), 1000);
      },

      filtersReset() {
        for (let key in this.filters.data) {
          this.filters.data[key] = '';
        }
        this.listRefresh();
      },

    }
  }
</script>


<style scoped>

</style>
