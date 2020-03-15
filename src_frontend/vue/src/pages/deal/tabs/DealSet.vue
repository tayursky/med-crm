<template>
  <div>
    <el-dialog class="form-block deal-set"
               :visible.sync="dialog_visible"
               :close-on-click-modal="false"
               :show-close="false"
               @keyup.esc="cancel"
               @keyup.enter="formSave('save')">

      <template slot="title">
        <span class="el-dialog__title">{{ title }}</span>
        <button type="button" class="el-dialog__headerbtn" title="Закрыть" @click="dealClose(false)">
          <i class="el-dialog__close el-icon el-icon-close"></i>
        </button>
        <button type="button" class="el-dialog__headerbtn" title="Обновить" @click="dealRefresh()">
          <i class="el-dialog__close el-icon el-icon-refresh"></i>
        </button>
      </template>

      <el-tabs v-model="activeTab" type="border-card" @tab-click="tabClick">

        <el-tab-pane name="deal" :label="tabs.deal.label">
          <deal-form v-if="tabs.deal.show"
                     app_label="deal"
                     model_name="deal"
                     :deal="deal"
                     :hide_title="true"
                     @setTitle="setTitle"
                     @tabsSet="tabsSet"/>
        </el-tab-pane>

        <el-tab-pane v-if="tabs.clients" name="clients" :label="tabs.clients.label">
          <tab-clients v-if="tabs.clients.show"
                       :deal="deal"
                       :tab="tabs.clients"
                       :permissions="permissions"/>
        </el-tab-pane>

        <el-tab-pane v-if="tabs.tasks" name="tasks" :label="tabs.tasks.label">
          <tab-tasks v-if="tabs.tasks.show"
                     :deal="deal"
                     :tab="tabs.tasks"
                     :permissions="permissions"/>
        </el-tab-pane>

        <el-tab-pane v-if="tabs.comments" name="comments" :label="tabs.comments.label">
          <tab-comments v-if="tabs.comments.show"
                        :deal="deal"
                        :tab="tabs.comments"
                        :permissions="permissions"/>
        </el-tab-pane>

        <el-tab-pane v-if="tabs.sms" name="sms" :label="tabs.sms.label">
          <tab-sms v-if="tabs.sms.show"
                   :deal="deal"
                   :tab="tabs.sms"/>
        </el-tab-pane>

        <el-tab-pane v-if="tabs.history" name="history" :label="tabs.history.label">
          <tab-history v-if="tabs.history.show"
                       :deal="deal"
                       :tab="tabs.history"/>
        </el-tab-pane>

      </el-tabs>

    </el-dialog>
  </div>
</template>


<script>
  import Vue from 'vue'
  import axios from 'axios'
  import VueAxios from 'vue-axios'
  import TabClients from "./TabClients";

  Vue.use(VueAxios, axios);

  export default {
    components: {TabClients},
    props: [],

    data() {
      return {
        deal: {'id': null},
        title: 'Карточка сделки',
        dialog_visible: false,
        activeTab: null,
        tabs: {},
        permissions: ['view', 'delete', 'add', 'change']
      }
    },
    computed: {},

    watch: {
      'dialog_visible'(value, fromValue) {
        if (!value) {
          this.$store.commit('set_deal', {'id': null});
        }
      },
      'deal': {
        handler: function (deal, fromDeal) {
          if (deal.id) {
            this.dialog_visible = true;
            if (deal.id === 'add') {
              this.tabReset();
            }
          } else {
            this.dialog_visible = false;
            this.tabReset();
          }
        },
        deep: true
      },
      'activeTab'(value, fromValue) {
        this.tabs[value].show = true;
        if (this.tabs[fromValue]) {
          this.tabs[fromValue].show = false;
        }
      },
    },

    created() {
      this.tabReset();
    },
    mounted() {
      this.store_subscribe = this.$store.subscribe((mutation, state) => {
        switch (mutation.type) {
          case 'set_deal':
            this.deal = state.deal.item;
            break;
        }
      });
    },
    beforeDestroy() {
      this.store_subscribe();
    },

    methods: {
      tabReset() {
        this.activeTab = 'deal';
        this.tabs = {'deal': {'label': 'Сделка', 'show': true}};
      },

      tabClick(tab, event) {
        // console.log('tabClick', tab.name);
      },

      setDialogVisible() {
      },

      setTitle(value) {
        this.title = value;
      },
      setVerboseName() {
      },

      dealRefresh() {
        this.tabReset();
        this.tabs.deal.show = false;
        setTimeout(function () {
          this.tabs.deal.show = true;
        }.bind(this), 1);
      },

      dealClose(refresh) {
        this.$store.commit('set_deal', {'id': null});
        if (refresh) {
          this.$store.commit('set_refresh_deals', refresh);
        }
        this.$store.commit('update_drag_drop', {'datetime': null, 'minutes': null,});
      },

      tabsSet(tabs) {
        this.tabs = tabs;
      }

    },
  }
</script>


<style>

</style>
