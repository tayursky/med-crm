<template>
  <div class="deal-content kanban deal-tasks">

    <div v-if="loading" class="loading"></div>
    <div v-else>
      <el-row class="directory__head">
        <div class="directory__title">{{ title }}</div>
        <div class="directory__buttons">
          <el-button icon="el-icon-close" title="Сбросить" @click="filtersReset"/>
          <el-button icon="el-icon-refresh-right" title="Обновить" @click="tasksRefresh"/>
        </div>
      </el-row>

      <filters :filters="filters" @changeFilters="filtersChange"/>

      <div class="deal-tasks__list">
        <div v-for="(key, status_index) in status_ordered"
             class="kanban__stage" :style="{width: stage_width}">
          <div class="kanban__stage__head"
               :style="{color: status[key].color,
                        backgroundColor: status[key].background_color}">
            {{ status[key].label }}
            <span v-if="tasks_filtered[key].length >0">({{ tasks_filtered[key].length }})</span>
          </div>

          <!-- Task -->
          <div v-for="(task, task_index) in tasks_filtered[key]"
               class="kanban__deal" :style="{borderColor: status[key].background_color}"
               @click="taskOpen(task)">
            <div class="deal-tasks__item__time">{{ task.time_planned }}</div>
            <div class="deal-tasks__item__title">{{ task.title }}</div>
            <div v-if="task.comment" class="deal-tasks__item__comment">{{ task.comment }}</div>
            <div class="deal-tasks__item__source">
              <template v-if="task.client">{{ task.client__cache.full_name }}</template>
              <template v-if="task.deal">{{ task.deal__cache.title }}</template>
            </div>
          </div>
          <!-- End task -->
        </div>
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
        title: null,
        loading: false,
        filters: null,
        filters_timeout: null,
        status: {},
        status_ordered: [],
        tasks: [],
        tasks_filtered: {},
        picker_options: {firstDayOfWeek: 1},
        permissions: ['add', 'change', 'delete', 'view']
      }
    },
    watch: {
      'refresh': function (value, fromValue) {
        if (value === true) {
          this.tasksRefresh();
        }
      },
      'title': function (value, fromValue) {
        document.title = value;
      },
      'tasks': function (value, fromValue) {
        this.tasks_filtered = {};
        for (let key in this.status_ordered) {
          let status = this.status_ordered[key];
          this.tasks_filtered[status] = value.filter(function (item) {
            return item.status === status;
          });
        }
      },

    },

    computed: {
      stage_width() {
        return 100 / this.status_ordered.length + '%'
      }
    },

    mounted() {
      this.store_subscribe = this.$store.subscribe((mutation, state) => {
        switch (mutation.type) {
          case 'set_refresh_clients':
            this.refresh = state.client.refresh;
            break;
          case 'set_refresh_deals':
            this.refresh = state.deal.refresh;
            break;
        }
      });
      this.tasksRefresh();
    },
    beforeDestroy() {
      this.store_subscribe();
    },

    methods: {

      getAjaxParams: function (from = null, string = false) {
        let params = {
          'get': true,
          'branch': this.$store.state.deal.branch.id
        };
        if (this.filters) {
          for (let filter_key in this.filters.data) {
            params[filter_key] = JSON.stringify(this.filters.data[filter_key]);
          }
        }
        return params;
      },

      tasksRefresh() {
        this.loading = true;
        Vue.axios
          .get(this.$store.getters.root_url + 'deal/task/', {params: this.getAjaxParams()})
          .then(response => {
            this.filters = response.data.filters;
            this.status = response.data.status;
            this.status_ordered = response.data.status_ordered;
            this.tasks = response.data.tasks;
            this.title = response.data.title;
          })
          .catch(error => {
            console.log(error);
          })
          .finally(() => {
            this.loading = false;
            this.$store.commit('set_refresh_clients', false);
            this.$store.commit('set_refresh_deals', false);
          });
      },

      taskOpen(task) {
        console.log('taskOpen', task.client, task.deal);
        if (task.client) {
          this.$store.commit('set_client', {'id': task.client, 'task': task.id});
        } else if (task.deal) {
          this.$store.commit('set_deal', {'id': task.deal, 'task': task.id});
        }
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
          this.tasksRefresh();
        }.bind(this), 1000);
      },

      filtersReset() {
        for (let key in this.filters.data) {
          this.filters.data[key] = '';
        }
        this.tasksRefresh();
      },

    }
  }
</script>


<style scoped>

</style>
