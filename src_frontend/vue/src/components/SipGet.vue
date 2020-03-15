<template>
  <div>

    <el-dialog class="form-block deal-set"
               :visible.sync="sip_show"
               :close-on-click-modal="false"
               :show-close="false"
               @keyup.esc="sipCancel">

      <template slot="title">
        <div class="clearfix">
          <span class="el-dialog__title">{{ title }}</span>
          <button type="button" class="el-dialog__headerbtn" title="Закрыть" @click="sipCancel">
            <i class="el-dialog__close el-icon el-icon-close"></i>
          </button>
          <button type="button" class="el-dialog__headerbtn" title="Обновить" @click="sipGetCalls">
            <i class="el-dialog__close el-icon el-icon-refresh"></i>
          </button>
        </div>
      </template>

      <div class="clearfix"></div>

      <div v-if="loading" class="modal-loading"></div>
      <table v-else class="sip-call__list">
        <tbody>
        <tr v-for="call in calls" class="sip-call__list__item">
          <td class="sip-call__list__item__time">{{ call.time }}</td>
          <td class="sip-call__list__item__phone">+{{ call.phone }}</td>
          <td class="sip-call__list__item__persons">
            <div v-for="person in call.persons" class="sip-call__list__item__person" @click="sipClient(person.id)">
              {{ person.cache.full_name }}
            </div>
            <template v-if="call.persons.length === 0">
              <div type="button" class="sip-call__list__item__btn_add"
                   title="Создать новую сделку" @click="dealAdd(call.phone)">
                <i class="el-icon-document-add"></i>
                <div class="txt">Создать сделку</div>
              </div>
              <div type="button" class="sip-call__list__item__btn_add"
                   title="Создать новую сделку" @click="clientAdd(call.phone)">
                <i class="el-icon-document-add"></i>
                <div class="txt">Создать карточку клиента</div>
              </div>
            </template>
          </td>
        </tr>
        </tbody>
      </table>

    </el-dialog>

  </div>
</template>


<script>
  import Vue from 'vue'
  import axios from 'axios'
  import VueAxios from 'vue-axios'

  Vue.use(VueAxios, axios);

  export default {
    props: ['sip_show', 'sip_limit'],
    data() {
      return {
        loading: false,
        dialog_visible: false,
        calls: []
      }
    },

    computed: {
      title() {
        return 'Список входящих звонков'
      },
    },

    watch: {
      'sip_show': function (value, fromValue) {
        if (value === true) {
          this.dialog_visible = true;
          this.sipGetCalls();
        }
      },
    },

    mounted() {
    },

    methods: {
      sipGetCalls() {
        this.dialog_visible = true;
        let url = this.$store.getters.root_url + 'sip/get_incoming/';
        let params = {'limit': this.sip_limit};
        this.loading = true;
        Vue.axios
          .get(url, {params: params})
          .then(response => {
            if (response.data.message) {
              this.$message({
                message: response.data.message.text,
                type: response.data.message.type,
                showClose: true
              });
            }
            this.calls = response.data.calls;
            if (this.calls.length === 1 && this.calls[0].persons.length === 1) {
              this.$emit('sipShow', false);
              this.$store.commit('set_client', {'id': this.calls[0].persons[0].id});
            }
          })
          .catch(error => {
            console.log(error);
          })
          .finally(() => {
            this.loading = false;
          });
      },

      sipCancel() {
        this.dialog_visible = false;
        this.$emit('sipShow', false);
      },

      sipClient(person_id) {
        this.dialog_visible = false;
        this.$emit('sipShow', false);
        this.$store.commit('set_client', {'id': person_id});
      },

      clientAdd(phone) {
        this.$emit('sipShow', false);
        this.$store.commit('set_client', {'id': 'add', 'phone': phone});
      },
      clientClose() {
        this.$emit('sipShow', false);
        this.$store.commit('set_client', {'id': null});
      },

      dealAdd(phone) {
        this.$emit('sipShow', false);
        this.$store.commit('set_deal', {'id': 'add', 'phone': phone});
        // this.$emit('sipDealAdd', phone);
      },

    }
  }
</script>


<style>

</style>
