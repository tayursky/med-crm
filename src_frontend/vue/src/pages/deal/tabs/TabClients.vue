<template>
  <div class="form_tab tab_clients">
    <div v-if="loading" class="modal-loading"></div>
    <div v-else>
      <div class="buttons">
        <!--el-button icon="el-icon-document-add" @click="clientEdit({id:'add'})"></el-button-->
        <el-button icon="el-icon-refresh" title="Обновить" @click="clientsRefresh"/>
      </div>

      <div v-if="client.id" class="form_tab__item">
        <the-form app_label="deal"
                  model_name="client"
                  :item="client"
                  :permissions="permissions"
                  @itemRefresh="clientsRefresh"
                  @itemClose="clientClose"/>
      </div>

      <table class="form_tab__table">
        <tbody>
        <tr v-for="(_client, _client_index) in clients"
            class="client" :class="{'hover': _client.id === client.id}">
          <td class="client__full_name" @click="clientEdit(_client)">{{ _client.full_name }}</td>
          <el-dropdown class="client__link client__doc">
            <el-button><i class="el-icon-document-copy el-icon--right"></i></el-button>
            <el-dropdown-menu slot="dropdown">
              <el-dropdown-item>
                <div @click="clientPaper(_client, 'contract')">
                  Договор (массаж)
                </div>
              </el-dropdown-item>
              <el-dropdown-item>
                <div @click="clientPaper(_client, 'consent_personal')">
                  Согласие (персон. данные)
                </div>
              </el-dropdown-item>
            </el-dropdown-menu>
          </el-dropdown>
          <td class="client__link" title="Карточка клиента" @click="clientOpen(_client)">
            <i class="el-icon el-icon-user"></i>
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
    props: ['deal', 'tab', 'permissions'],

    data() {
      return {
        loading: false,
        service_set: {},
        clients: [],
        client: {},
      }
    },

    computed: {},

    watch: {},

    mounted() {
      this.clientsRefresh();
    },

    methods: {
      clientsRefresh(client_id) {
        this.loading = true;
        if (typeof client_id !== 'number') {
          client_id = null;
        }
        let params = {
          'deal': this.deal ? this.deal.id : null,
        };
        Vue.axios
          .get(this.$store.getters.root_url + 'directory/client/', {params: params})
          .then(response => {
            this.clients = response.data.items;
          })
          .catch(error => {
            alert(error);
          })
          .finally(() => {
            this.loading = false;
            this.client = {'id': client_id};
          });
      },

      clientEdit(client) {
        this.client = client;
      },
      clientClose(client_id) {
        this.clientsRefresh(client_id);
      },
      clientOpen(client) {
        this.$store.commit('set_deal', {'id': null});
        this.$store.commit('set_client', {'id': client.id});
      },

      clientPaper(client, doc_type) {
        console.log('clientPaper', doc_type);
        let url = this.$store.getters.root_url + 'deal/doc' +
          '?deal=' + this.deal.id
          + '&person=' + client.id
          + '&doc_type=' + doc_type;
        window.open(url, "_blank");
      }

    },
  }
</script>


<style>

</style>
