<template>
  <div class="form_tab tab_deals">
    <div v-if="loading" class="modal-loading"></div>
    <div v-else>
      <div class="buttons">
        <el-button icon="el-icon-document-add" @click="dealEdit({id:'add'})"></el-button>
        <el-button icon="el-icon-refresh" title="Обновить" @click="dealsRefresh"/>
      </div>

      <deal-form v-if="deal.id"
                 :deal="deal"
                 :client="client"
                 :permissions="permissions"
                 @dealClose="dealClose"/>

      <table class="form_tab__table">
        <tbody>
        <tr v-for="(item, item_index) in deals"
            class="deal" :class="{'hover': item.id === deal.id}">
          <td class="deal__title"
              :style="{backgroundColor: stages[item.step].background_color,
                       color: stages[item.step].color}"
              @click="dealEdit(item)">
            {{ item.title }}
          </td>
          <td class="deal__persons" @click="dealEdit(item)">
            <div v-for="(person, person_key) in item.persons" class="deal__persons__item">
              {{ person.full_name }} <span v-if="person.phones">({{ person.phones }})</span>
            </div>
          </td>
          <td class="deal__link" title="Открыть сделку" @click="dealOpen(item)">
            <i class="el-icon el-icon-tickets"></i>
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
    props: ['client', 'tab', 'permissions'],

    data() {
      return {
        loading: false,
        stages: {},
        deals: [],
        deal: {},
      }
    },

    computed: {},

    watch: {},

    mounted() {
      this.dealsRefresh();
    },

    methods: {
      dealsRefresh(deal_id) {
        this.loading = true;
        if (typeof deal_id !== 'number') {
          deal_id = null;
        }
        let params = {
          'client': this.client ? this.client.id : null,
        };
        Vue.axios
          .get(this.$store.getters.root_url + 'deal/list/', {params: params})
          .then(response => {
            this.deals = response.data.deals;
            this.stages = response.data.stages;
          })
          .catch(error => {
            console.log(error);
          })
          .finally(() => {
            this.loading = false;
            this.deal = {'id': deal_id}
          });
      },

      dealEdit(deal) {
        this.deal = deal;
      },
      dealClose(deal_id) {
        this.dealsRefresh(deal_id);
      },
      dealOpen(deal) {
        this.$store.commit('set_client', {'id': null});
        this.$store.commit('set_deal', {'id': deal.id});
      }

    },
  }
</script>


<style>

</style>
