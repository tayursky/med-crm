<template>
  <div class="form_tab tab_history">
    <div v-if="loading" class="modal-loading"></div>
    <div v-else>
      <div class="buttons">
        <el-button icon="el-icon-refresh" title="Обновить" @click="historyRefresh"/>
      </div>
      <table class="form_tab__table">
        <tbody>
        <tr v-for="(history, history_index) in history_list" class="history">
          <td class="history__time" :title="history.history_user">{{ history.time }}</td>
          <td class="history__value">
            <div class="history__value__title">{{ history.label }}</div>
            <div class="history__value__text">
              <span v-if="history.old">{{ history.old }} &rarr; </span>
              <span v-if="history.new">{{ history.new }}</span>
            </div>
          </td>
          <td class="history__history_user" :title="history.history_user"><i class="el-icon-user"></i></td>
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
    props: ['client', 'deal', 'tab'],
    data() {
      return {
        loading: false,
        history_list: [],
      }
    },
    computed: {},
    watch: {},
    mounted() {
      this.historyRefresh();
    },
    methods: {
      historyRefresh() {
        this.loading = true;
        let params = {
          'client': this.client ? this.client.id : null,
          'deal': this.deal ? this.deal.id : null
        };
        let url = this.$store.getters.root_url + 'deal/history/';
        Vue.axios.get(url, {params: params})
          .then(response => {
            this.history_list = response.data.history;
            this.loading = false;
          })
          .catch(error => {
            this.loading = false;
            console.log(error);
          });
      },
    },
  }
</script>


<style>

</style>
