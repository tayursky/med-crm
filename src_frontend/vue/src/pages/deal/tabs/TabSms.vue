<template>
  <div class="form_tab tab_sms">
    <div v-if="loading" class="modal-loading"></div>
    <div v-else>
      <div class="buttons">
        <div class="float-left">
          <el-button v-if="permissions.indexOf('mlm.send_invite') > -1"
                     icon="el-icon-s-promotion"
                     title="МЛМ-приглашение"
                     @click="mlmInvite">МЛМ-приглашение
          </el-button>
        </div>
        <div class="float-right">
          <el-button v-if="deal" icon="el-icon-d-arrow-right" title="Отправить еще раз" @click="smsResend"/>
          <el-button icon="el-icon-refresh" title="Обновить" @click="smsRefresh"/>
        </div>
        <div class="clearfix"></div>
      </div>

      <table class="form_tab__table">
        <tbody>
        <tr v-for="(sms, sms_index) in sms_list" class="sms">
          <td class="sms__time">{{ sms.time_created.slice(0, 16) }}</td>
          <td class="sms__value">
            <div class="sms__value__title">{{ sms.id }}, {{ sms.phone }} ({{ sms.status_title }})</div>
            <div class="sms__value__text">{{ sms.text }}</div>
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
    props: ['client', 'deal', 'tab'],
    data() {
      return {
        loading: false,
        permissions: [],
        sms_list: [],
      }
    },
    computed: {},
    watch: {},
    mounted() {
      this.smsRefresh();
    },
    methods: {
      smsRefresh() {
        this.loading = true;
        let params = {
          'client': this.client ? this.client.id : null,
          'deal': this.deal ? this.deal.id : null
        };
        let url = this.$store.getters.root_url + 'sms/';
        Vue.axios
          .get(url, {params: params})
          .then(response => {
            this.permissions = response.data.permissions;
            this.sms_list = response.data.items;
          })
          .catch(error => {
            alert(error);
          })
          .finally(() => {
            this.loading = false;
          });
      },

      smsResend() {
        if (!confirm('Отправить смс еще раз?')) {
          return
        }
        this.loading = true;
        let params = {
          'client': this.client ? this.client.id : null,
          'deal': this.deal ? this.deal.id : null
        };
        let url = this.$store.getters.root_url + 'sms/resend/';
        Vue.axios
          .get(url, {params: params})
          .then(response => {
          })
          .catch(error => {
            alert(error);
          })
          .finally(() => {
            this.smsRefresh();
          });
      },

      mlmInvite() {
        this.loading = true;
        let params = {
          'channel': 'sms',
          'deal': this.deal ? this.deal.id : null,
          'person': this.client ? this.client.id : null,
        };
        let url = this.$store.getters.root_url + 'mlm/invite_send/';
        Vue.axios
          .get(url, {params: params})
          .then(response => {
            if (response.data.message) {
              this.$message({
                message: response.data.message.text, type: response.data.message.type, showClose: true
              });
            }
          })
          .catch(error => {
            alert(error);
          })
          .finally(() => {
            this.loading = false;
            this.smsRefresh();
          });
      },
    },
  }
</script>


<style>

</style>
