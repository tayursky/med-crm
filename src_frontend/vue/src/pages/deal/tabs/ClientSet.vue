<template>
  <div>
    <el-dialog class="form-block client-set"
               :visible.sync="dialog_visible"
               :close-on-click-modal="false"
               :show-close="false"
               @keyup.esc="cancel"
               @keyup.enter="formSave('save')">

      <template slot="title">
        <span class="el-dialog__title">{{ title }}</span>
        <button type="button" class="el-dialog__headerbtn" title="Закрыть" @click="clientClose(false)">
          <i class="el-dialog__close el-icon el-icon-close"></i>
        </button>
        <button type="button" class="el-dialog__headerbtn" title="Обновить" @click="clientRefresh()">
          <i class="el-dialog__close el-icon el-icon-refresh"></i>
        </button>
      </template>

      <el-tabs v-model="activeTab" type="border-card" @tab-click="tabClick">

        <el-tab-pane name="client" label="Персональные данные">
          <the-form v-if="tabs.client.show && client.id"
                    app_label="deal"
                    model_name="client"
                    :item="client"
                    :permissions="permissions"
                    @setDialogVisible="setDialogVisible"
                    @setVerboseName="setVerboseName"
                    @setTitle="setTitle"
                    @tabsSet="tabsSet"
                    @itemRefresh="clientRefresh"
                    @itemClose="clientClose"/>
        </el-tab-pane>

        <el-tab-pane v-if="tabs.deals" name="deals" :label="tabs.deals.label">
          <tab-deals v-if="tabs.deals.show"
                     :client="client"
                     :tab="tabs.deals"
                     :permissions="permissions"/>
        </el-tab-pane>

        <el-tab-pane v-if="tabs.tasks" name="tasks" :label="tabs.tasks.label">
          <tab-tasks v-if="tabs.tasks.show"
                     :client="client"
                     :tab="tabs.tasks"
                     :permissions="permissions"/>
        </el-tab-pane>

        <el-tab-pane v-if="tabs.comments" name="comments" :label="tabs.comments.label">
          <tab-comments v-if="tabs.comments.show"
                        :client="client"
                        :tab="tabs.comments"
                        :permissions="permissions"/>
        </el-tab-pane>

        <el-tab-pane v-if="tabs.sms" name="sms" :label="tabs.sms.label">
          <tab-sms v-if="tabs.sms.show"
                   :client="client"
                   :tab="tabs.sms"/>
        </el-tab-pane>

        <el-tab-pane v-if="tabs.history" name="history" :label="tabs.history.label">
          <tab-history v-if="tabs.history.show"
                       :client="client"
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
  import TabDeals from './TabDeals'

  Vue.use(VueAxios, axios);

  export default {
    components: {TabDeals},
    props: ['permissions'],

    data() {
      return {
        client: {'id': null},
        activeTab: 'client',
        title: '',
        dialog_visible: false,
        tabs: {},
      }
    },
    computed: {},

    watch: {
      'dialog_visible'(value, fromValue) {
        if (!value) {
          this.$emit('itemClose');
          // this.$emit('itemClose', false);
        }
      },
      'client'(client, fromClient) {
        // console.log('watch client', client, fromClient);
        this.activeTab = 'client';
        if (client.id) {
          this.dialog_visible = true;
          if (client.id === 'add') {
            this.tabReset();
          }
        } else {
          this.dialog_visible = false;
          this.tabReset();
        }
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
          case 'set_client':
            // console.log('store_subscribe', this.deal);
            this.client = state.client.item;
            break;
        }
      });
    },
    beforeDestroy() {
      this.store_subscribe();
    },

    methods: {
      tabReset() {
        this.activeTab = 'client';
        this.tabs = {'client': {'label': 'Карточка клиента', 'show': true}};
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
      clientRefresh(value) {
        this.tabReset();
        this.tabs.client.show = false;
        setTimeout(function () {
          this.tabs.client.show = true;
        }.bind(this), 1);
      },
      clientClose(refresh) {
        this.$store.commit('set_client', {'id': null});
        this.$store.commit('set_refresh_clients', true);
      },
      tabsSet(tabs) {
        this.tabs = tabs;
      }
    },
  }
</script>


<style>

</style>
