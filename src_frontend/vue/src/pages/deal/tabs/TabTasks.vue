<template>
  <div class="form_tab tab_tasks">
    <div v-if="loading" class="modal-loading"></div>
    <div v-else>
      <div class="buttons">
        <el-button icon="el-icon-document-add" @click="taskEdit({id:'add'})"></el-button>
        <el-button icon="el-icon-refresh" title="Обновить" @click="taskRefresh"/>
      </div>

      <div v-if="item.id" class="el-tabs__form">
        <the-form app_label="directory"
                  model_name="dealtask"
                  :item="item"
                  :permissions="permissions"
                  @itemRefresh="taskRefresh"
                  @itemClose="taskRefresh"/>
      </div>

      <table v-if="tasks.length > 0" class="form_tab__table">
        <thead>
        <tr>
          <td>Время</td>
          <td class="text-right">Источник</td>
          <td>Задача</td>
        </tr>
        </thead>
        <tbody>
        <tr v-for="(task, task_index) in tasks"
            class="task" :class="{'hover': task.id === item.id}"
            @click="taskEdit(task)">
          <td class="task__time"
              :style="{backgroundColor: status[task.status].background_color,
              color: status[task.status].color}">
            {{ task.time_planned }}
          </td>
          <td class="task__source">
            <template v-if="task.client">{{ task.client__cache.full_name }}</template>
            <template v-if="task.deal">{{ task.deal__cache.title }}</template>
          </td>
          <td>
            <div class="task__title">{{ task.title }}</div>
            <div v-if="task.comment" class="task__comment">{{ task.comment }}</div>
          </td>
        </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>


<script>
  import Vue from 'vue'
  import axios from 'axios'
  import VueAxios from 'vue-axios'

  Vue.use(VueAxios, axios);

  export default {
    props: ['client', 'deal', 'tab', 'permissions'],

    data() {
      return {
        loading: false,
        tasks: [],
        item: {},
        status: {},
        service_set: {},
      }
    },
    computed: {},

    watch: {
      'item': function (value, fromValue) {
        if (value === null) {
          this.taskRefresh();
        }
      },
    },

    mounted() {
      this.taskRefresh();
    },

    methods: {
      taskRefresh() {
        this.loading = true;
        let params = {
          'client': this.client ? this.client.id : null,
          'deal': this.deal ? this.deal.id : null
        };
        let url = this.$store.getters.root_url + 'deal/task/';
        Vue.axios.get(url, {params: params})
          .then(response => {
            this.item = {};
            this.tasks = response.data.tasks;
            this.status = response.data.status;
            this.service_set = response.data.service_set;
            this.loading = false;
          })
          .catch(error => {
            this.loading = false;
            console.log(error);
          });
      },

      taskEdit(task) {
        if (task.id === 'add') {
          task.client = this.client ? this.client.id : null;
          task.deal = this.deal ? this.deal.id : null;
        }
        this.item = task;
      },

    },
  }
</script>


<style>

</style>
