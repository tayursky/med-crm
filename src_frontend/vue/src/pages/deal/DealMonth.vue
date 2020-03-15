<template>
  <div class="deal-content">

    <h1>Календарь на месяц</h1>

    <div v-if="loading" class="loading"></div>
    <div v-else class="i-month">

      <div v-if="branch.id" class="deal-content__top">
        <div class="deal-content__top__service_select">
          <el-select v-model="branch.id" filterable placeholder="">
            <el-option v-for="branch_id in branch_set.ordered"
                       :key="branch_id"
                       :value="branch_id"
                       :label="branch_set.branches[branch_id].label"/>
          </el-select>
          <el-button icon="el-icon-refresh" title="Обновить" @click="branchLoad()"/>
        </div>

        <div v-if="month_set" class="float-right">
          <div class="deal-content__top__title">{{ month_set.year }} {{ month_set.month_name }}</div>
          <el-button icon="el-icon-refresh" title="Обновить" @click="monthLoad()"/>
        </div>
      </div>

      <template v-if="month_set">
        <div class="i-month__header">
          <div class="float-right">
            <el-button-group>
              <button type="button" class="el-button el-button--plain el-button--mini" @click="monthLoad('current')">
                Текущий месяц
              </button>
              <button type="button" class="el-button" title="Предыдущий месяц" @click="monthLoad('prev')">
                <i class="el-icon-d-arrow-left"></i>
              </button>
              <button type="button" class="el-button" title="Следующий месяц" @click="monthLoad('next')">
                <i class="el-icon-d-arrow-right"></i>
              </button>
            </el-button-group>
          </div>
          <div class="clearfix"></div>
        </div>

        <table cellspacing="0" cellpadding="0" class="i-month__table">
          <thead>
          <th v-for="(head, head_index) in month_set.week_head">{{ head }}</th>
          <th></th>
          </thead>

          <tbody>
          <tr v-for="(week, week_index) in month_set.weeks">
            <td v-for="(day, day_index) in week"
                class="i-month__table__td" :class="{'today': day.label === month_set.today}">
              <div class="month-item">
                <div class="month-day" type="date" @click="goDay(day.iso)">
                  <div class="month-day__day" :class="{'month-day__other': day.month !== month_set.month}"
                       title="Расписание на день">{{ parseInt($moment(day.iso).format().slice(8, 10)) }}
                  </div>
                </div>
              </div>

              <template v-if="month_set.deals[day.iso]">
                <template v-for="(count, step) in month_set.deals[day.iso]">
                  <div v-if="stages[step]" class="month-deals-count"
                       :style="{backgroundColor: stages[step].background_color, color: stages[step].color}">
                    {{ count }}
                  </div>
                </template>
              </template>
            </td>
            <td>
              <div class="i-month__table__week"
                   title="Расписание на неделю"
                   @click="goWeek(week[0].iso)">
                <i class="el-icon-d-arrow-right"></i></div>
            </td>
          </tr>
          </tbody>
        </table>
      </template>


    </div>

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
        loading: true,
        branch: {id: null, group_services: []},
        branch_set: {group_services: []},
        branch_group_services_selected: [],
        branch_masters_selected: [],
        stages: [],
        searching: false,
        service_set: null,
        service: {'id': null, list: []},
        get_month: null,
        month_set: null,
      }
    },

    watch: {
      'branch': {
        handler: function (branch, fromValue) {
          this.branch_group_services_selected = [];
          this.branch_masters_selected = [];
          if (branch.id) {
            this.$store.commit('set_branch', {'id': branch.id});
          } else {
            this.$store.commit('set_branch', {'id': null});
          }
          this.monthLoad();
        },
        deep: true
      },

    },

    computed: {},

    created() {
    },

    mounted() {
      this.store_subscribe = this.$store.subscribe((mutation, state) => {
        switch (mutation.type) {
          case 'set_service_id':
            console.log('switch');
            this.monthLoad();
            break;
        }
      });
      document.title = 'Календарь на месяц';
      this.branchLoad();
    },

    methods: {

      branchLoad() {
        this.loading = true;
        Vue.axios.get(this.$store.getters.root_url + 'deal/get_branch_list/', {params: {'get': true}})
          .then(response => {
            this.branch_set = response.data;
            if (this.$store.state.deal.branch.id) {
              this.branch = this.branch_set.branches[this.$store.state.deal.branch.id];
            } else {
              this.branch = this.branch_set.branches[this.branch_set.ordered[0]];
            }
            this.branch_group_services_selected = [];
            this.branch_masters_selected = [];
          })
          .catch(error => {
            console.log(error);
          })
          .finally(() => {
            this.monthLoad();
          });
      },

      monthLoad(step) {
        this.loading = true;
        let params = {
          'current_day': this.$store.state.deal.current_day,
          'step': step || null,
          'branch': this.branch.id,
        };
        Vue.axios
          .get(this.$store.getters.root_url + 'deal/month/', {params: params})
          .then(response => {
            this.$store.commit('set_current_day', response.data.current_day);
            this.month_set = response.data.month_set;
            this.stages = response.data.stages;
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

      goWeek(day) {
        this.$store.commit('set_current_day', day);
        this.$router.push({name: 'deal_schedule'});
      },

      goDay(day) {
        this.$store.commit('set_current_day', day);
        this.$router.push({name: 'deal_schedule'});
      },
    }
  }
</script>


<style scoped>

</style>
