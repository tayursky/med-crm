<template>
  <div>
    <div class="loading" v-if="loading"></div>

    <div v-else class="form-block mlm-agent">

      <div style="padding: 0 0 5px; display: inline-block; width: 100%;">
        <div class="float-right">
          <el-button icon="el-icon-refresh" @click="agentLoad"></el-button>
        </div>
      </div>

      <div v-if="person" class="mlm-agent__person" @click="clientEdit">
        <div class="mlm-agent__person__title">
          {{ person.full_name }}<i class="el-icon el-icon-edit"></i>
        </div>
        <div class="mlm-agent__person__item">День рождения: {{ person.birthday }}</div>
        <div class="mlm-agent__person__item">Телефон: {{ person.phone }}</div>
      </div>

      <div v-if="agent" class="mlm-agent__agent" @click="agentEdit">
        <div class="mlm-agent__person__title">
          <strong>{{ agent.position__label }}</strong><i class="el-icon el-icon-edit"></i>
        </div>
        <div v-if="agent.parent" class="mlm-agent__person__item">
          Менеджер: {{ agent.parent.full_name }} ({{ agent.parent.code }})
        </div>
        <div v-if="agent.referrer" class="mlm-agent__person__item">
          Пригласил: {{ agent.referrer }}
        </div>
        <div class="mlm-agent__person__item">Промокод: {{ agent.code }}</div>
        <div class="mlm-agent__person__item">Скидка: {{ agent.discount }}</div>
        <div class="mlm-agent__person__item">
          Процент за уровни: {{ agent.level_1 }} - {{ agent.level_2 }} - {{ agent.level_3 }}
        </div>
        <div class="mlm-agent__person__item">Номер карты: {{ agent.bank_account }}</div>
        <div class="mlm-agent__person__item">Имя на карте: {{ agent.bank_account_fio }}</div>
        <div class="mlm-agent__person__item">Комментарий: {{ agent.comment }}</div>
      </div>

      <div v-if="agent" class="mlm-agent__balance">
        <template v-if="agent.cache.manager_income">
          <div class="mlm-agent__balance__item">Начислено как менеджеру: {{ agent.cache.manager_income }}</div>
          <div class="mlm-agent__balance__item">Начислено за приглашения: {{ agent.cache.invite_cost }}</div>
        </template>
        <div class="mlm-agent__balance__item">Всего начислено: {{ agent.cache.total }}</div>
        <div class="mlm-agent__balance__item">Выплачено: {{ agent.cache.invite_paid }}</div>
        <div class="mlm-agent__balance__item">Баланс: {{ agent.cache.invite_balance }}</div>
      </div>

      <the-dialog app_label="directory"
                  :model_name="model_name"
                  :item="agent_item"
                  :permissions="permissions"
                  @itemClose="agentClose"/>


      <el-tabs v-model="activeTab" type="border-card">

        <el-tab-pane v-if="agent && agent.position === 'manager'" name="child_agents_total" label="Закрытые периоды">
          <el-row class="directory__head">
            <div v-if="!child_agents_total.loading" class="directory__total">
              Начислено: {{ agent.cache.manager_income }}
            </div>
            <div class="float-right">
              <el-button icon="el-icon-refresh" title="Обновить" @click="childAgentsTotalLoad()"/>
            </div>
          </el-row>
          <template v-if="!child_agents_total.loading">
            <br/>
            <data-table :headers="child_agents_total.headers"
                        :items="child_agents_total.items"
                        :loading="child_agents_total.loading"/>
          </template>
        </el-tab-pane>

        <el-tab-pane v-if="agent && agent.position === 'manager'"
                     name="child_agents" label="По месяцам">
          <el-row class="directory__head">
            <div v-if="!child_agents.loading" class="directory__total">
              Агентов: {{ child_agents.count }} |
              Оборот: {{ child_agents.cost__total }} |
              Процент: {{ child_agents.manager_percent }}% |
              Начислено: {{ child_agents.salary }}
            </div>

            <div class="float-right">
              <div v-if="month_set" class="deal-content__top__title">
                {{ month_set.year }} {{ month_set.month_name }}
              </div>
              <el-button icon="el-icon-refresh" title="Обновить" @click="childAgentsLoad()"/>

              <div v-if="month_set" class="i-month__header">
                <div class="float-right">
                  <el-button-group>
                    <button type="button" class="el-button el-button--plain el-button--mini"
                            @click="childAgentsLoad('current')">
                      Текущий месяц
                    </button>
                    <button type="button" class="el-button" title="Предыдущий месяц" @click="childAgentsLoad('prev')">
                      <i class="el-icon-d-arrow-left"></i>
                    </button>
                    <button type="button" class="el-button" title="Следующий месяц" @click="childAgentsLoad('next')">
                      <i class="el-icon-d-arrow-right"></i>
                    </button>
                  </el-button-group>
                </div>
                <div class="clearfix"></div>
              </div>
            </div>
          </el-row>
          <template v-if="!child_agents.loading">
            <data-table :headers="child_agents.headers"
                        :items="child_agents.items"
                        :loading="child_agents.loading"/>
            <!--paging :paging="child_agents.paging" @changePage="childAgentsPageChange"/-->
          </template>
        </el-tab-pane>

        <el-tab-pane name="invites" label="Приглашения">
          <el-row class="directory__head">
            <div class="directory__total">Всего: {{ invites.count }}</div>
            <div class="directory__buttons">
              <el-button icon="el-icon-refresh" title="Обновить" @click="invitesLoad"/>
            </div>
          </el-row>
          <template v-if="!invites.loading">
            <data-table :headers="invites.headers"
                        :items="invites.items"
                        :loading="invites.loading"
                        @editItem="inviteEdit"/>
            <paging :paging="invites.paging" @changePage="invitesPageChange"/>
          </template>
        </el-tab-pane>

        <el-tab-pane name="payments" label="Выплаты">
          <el-row class="directory__head">
            <div class="directory__total">Всего: {{ payments.count }}</div>
            <div class="directory__buttons">
              <el-button icon="el-icon-document-add" title="Добавить" @click="paymentAdd"/>
              <el-button icon="el-icon-refresh" title="Обновить" @click="paymentsLoad"/>
            </div>
          </el-row>
          <template v-if="!payments.loading">
            <data-table :headers="payments.headers"
                        :items="payments.items"
                        :loading="payments.loading"
                        @editItem="paymentEdit"/>
            <paging :paging="payments.paging" @changePage="paymentsPageChange"/>
          </template>
        </el-tab-pane>

      </el-tabs>

    </div>

    <the-dialog app_label="directory"
                model_name="agentpayment"
                :item="payment"
                :permissions="permissions"
                @itemClose="paymentClose"/>

  </div>
</template>


<script>
  import Vue from 'vue'
  import axios from 'axios'
  import VueAxios from 'vue-axios'

  Vue.use(VueAxios, axios);

  export default {
    data() {
      return {
        centerDialogVisible: false,
        activeTab: '',
        loading: false,
        agent: null,
        person: null,
        verbose_name: '',
        url: '',
        model_name: 'agent',
        agent_item: {},
        permissions: [],
        month_set: null,
        child_agents: {'loading': true},
        child_agents_total: {'loading': true},
        invites: {'loading': true},
        payments: {'loading': true},
        payment: {}
      }
    },

    computed: {
      agent_id() {
        return this.$route.params.agent_id
      },
    },

    watch: {
      activeTab(value, fromValue) {
        console.log('watch', value);
        if (value === 'child_agents_total') this.childAgentsTotalLoad();
        else if (value === 'child_agents') this.childAgentsLoad();
        else if (value === 'payments') this.paymentsLoad();
        else if (value === 'invites') this.invitesLoad();
      },
      centerDialogVisible(toVal, fromVal) {
        if (toVal === false) {
          this.formCancel();
        }
      },
    },

    mounted() {
      this.store_subscribe = this.$store.subscribe((mutation, state) => {
        switch (mutation.type) {
          case 'set_refresh_clients':
            this.agentLoad();
            break;
        }
      });
      this.agentLoad();
    },
    beforeDestroy() {
      this.store_subscribe();
    },

    methods: {

      agentLoad() {
        this.centerDialogVisible = true;
        this.loading = true;
        let params = {'get': true};
        let url = this.$store.getters.root_url + 'company/mlm_agent/' + this.agent_id + '/';
        Vue.axios.get(url, {params: params})
          .then(response => {
            this.agent = response.data.agent;
            this.person = response.data.person;
            this.verbose_name = response.data.form.verbose_name;
            this.data = response.data.form.data;
            this.ordered_fields = response.data.form.ordered_fields;
            this.fields = response.data.form.fields;
            this.errors = response.data.form.errors;
          })
          .catch(error => {
            alert(error);
          })
          .finally(() => {
            this.loading = false;
            if (this.agent.position === 'manager') {
              this.activeTab = 'child_agents_total';
            } else {
              this.activeTab = 'invites';
            }
          });
      },

      childAgentsTotalLoad() {
        this.centerDialogVisible = true;
        this.child_agents_total.loading = true;
        let params = {
          'get': true,
          'agent': this.agent_id,
        };
        if (this.month_set) {
          params['day'] = this.month_set.day;
        }
        let url = this.$store.getters.root_url + 'company/mlm_agent/' + this.agent_id + '/child_agents_total/';
        Vue.axios
          .get(url, {params: params})
          .then(response => {
            this.month_set = response.data.month_set;
            this.child_agents_total.headers = response.data.headers;
            this.child_agents_total.items = response.data.items;
          })
          .catch(error => {
            alert(error);
          })
          .finally(() => {
            this.child_agents_total.loading = false;
          });
      },

      childAgentsLoad(get_month) {
        this.centerDialogVisible = true;
        this.child_agents.loading = true;
        let params = {
          'get': true,
          'agent': this.agent_id,
          'get_month': get_month,
        };
        if (this.month_set) {
          params['day'] = this.month_set.day;
        }
        let url = this.$store.getters.root_url + 'company/mlm_agent/' + this.agent_id + '/child_agents/';
        Vue.axios
          .get(url, {params: params})
          .then(response => {
            this.month_set = response.data.month_set;
            this.child_agents = response.data.child_agents;
          })
          .catch(error => {
            alert(error);
          })
          .finally(() => {
            this.child_agents.loading = false;
          });
      },
      childAgentsPageChange(page) {
        this.child_agents.paging.page = page;
        this.childAgentsLoad();
      },

      invitesLoad() {
        this.centerDialogVisible = true;
        this.invites.loading = true;
        let params = {'get': true, 'agent': this.agent_id};
        let url = this.$store.getters.root_url + 'directory/invite/';
        Vue.axios.get(url, {params: params})
          .then(response => {
            this.invites = {
              'filters': response.data.filters,
              'headers': response.data.headers,
              'items': response.data.items,
              'count': response.data.count,
              'permissions': response.data.permissions,
              'paging': response.data.paging
            };
          })
          .catch(error => {
            alert(error);
          })
          .finally(() => {
            this.invites.loading = false;
          });
      },
      invitesPageChange(page) {
        this.invites.paging.page = page;
        this.invitesLoad();
      },
      inviteEdit(item) {
        this.$store.commit('set_deal', {'id': item['deal_id']});
      },

      paymentsLoad() {
        this.centerDialogVisible = true;
        this.payments.loading = true;
        let params = {'get': true, 'agent': this.agent_id};
        let url = this.$store.getters.root_url + 'directory/agentpayment/';
        Vue.axios.get(url, {params: params})
          .then(response => {
            this.payments = {
              'filters': response.data.filters,
              'headers': response.data.headers,
              'items': response.data.items,
              'count': response.data.count,
              'permissions': response.data.permissions,
              'paging': response.data.paging
            };
          })
          .catch(error => {
            alert(error);
          })
          .finally(() => {
            this.payments.loading = false;
          });
      },
      paymentsPageChange(page) {
        this.payments.paging.page = page;
        this.paymentsLoad();
      },
      paymentEdit(item) {
        this.payment = {'id': item.id};
      },
      paymentAdd() {
        this.payment = {'id': 'add', 'initial': {'agent': this.agent_id}};
      },
      paymentClose() {
        this.payment = {};
        this.paymentsLoad();
        this.agentLoad();
      },

      getFormData(object) {
        let formData = new FormData();
        formData.append('csrfmiddlewaretoken', this.csrf_token);
        Object.keys(object).forEach(
          key => formData.append(key, object[key])
        );
        return formData;
      },

      formSave(action) {
        this.loading = true;
        let url = this.$store.getters.root_url + 'company/mlm_agent/' + this.agent_id + '/' + action + '/';
        if (action === 'delete' && !confirm('Удалить?')) {
          return
        }
        Vue.axios.post(url, this.getFormData(this.data))
          .then(response => {
            if (response.data.errors) {
              this.errors = response.data.errors;
            } else {
              this.errors = {};
              this.centerDialogVisible = false;
              if (response.data.url) {
                window.location = response.data.url;
              }
            }
            if (response.data.message) {
              this.$message({
                message: response.data.message.text,
                type: response.data.message.type,
                showClose: true,
              });
            }
          })
          .catch(error => {
            alert(error);
          })
          .finally(() => {
            this.loading = false;
          });
      },

      changeData(key, value) {
        this.data[key] = value;
      },

      formCancel() {
        this.loading = false;
        this.$emit('itemClose');
      },

      clientEdit() {
        this.$store.commit('set_client', {'id': this.person.id});
      },

      agentEdit() {
        this.agent_item = {'id': this.agent.id};
      },
      agentClose(reload = true) {
        this.agent_item = {};
        if (reload) {
          this.agentLoad();
        }
      },

      clone(obj) {
        if (null == obj || "object" != typeof obj) return obj;
        let copy = obj.constructor();
        for (let attr in obj) {
          if (obj.hasOwnProperty(attr)) copy[attr] = obj[attr];
        }
        return copy;
      },

    }
  }
</script>


<style>

</style>
