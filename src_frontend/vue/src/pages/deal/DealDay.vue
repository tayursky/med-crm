<template>

  <div class="deal-content">
    <h1>{{ title }}</h1>
    <div v-if="loading" class="loading"></div>

    <div v-else class="i-day">

      <div class="deal-content__top">
        <div class="deal-content__top__service_select">
          <el-select v-model="service_selected" filterable placeholder="">
            <el-option v-for="item in service_list"
                       :key="item.value"
                       :label="item.label"
                       :value="item.value">
            </el-option>
          </el-select>
        </div>

        <div class="float-right" v-if="day_set">
          <button type="button" class="el-button" @click="dayExcel()">
            <div class="el-button__text">Выгрузить в exel</div>
          </button>
          <div class="deal-content__top__title">{{ day_set.title }}</div>
          <el-button icon="el-icon-refresh" title="Обновить" @click="dayLoad()"/>
        </div>
      </div>

      <template v-if="day_set">

        <div class="i-day__header">
          <router-link tag="button" class="el-button" :to="{name: 'schedule'}">
            <i class="el-icon-date"></i>Неделя
          </router-link>
          <div class="float-right">
            <el-button-group>
              <button type="button" class="el-button" @click="dayLoad('current')">
                Сегодня
              </button>
              <button type="button" class="el-button" title="Предыдущий день" @click="dayLoad('prev')">
                <i class="el-icon-d-arrow-left"></i>
              </button>
              <button type="button" class="el-button" title="Следующий день" @click="dayLoad('next')">
                <i class="el-icon-d-arrow-right"></i>
              </button>
            </el-button-group>
          </div>
        </div>

        <div v-if="day_set.master_full_name" class="i-day__master">{{ day_set.master_full_name }}</div>

        <table v-if="day_set.timing" cellspacing="0" cellpadding="0" class="i-day__table">
          <tbody>

          <template v-for="time_key in day_set.timing_sorted">

            <!-- Group -->
            <tr v-if="Object.keys(day_set.groups).indexOf(time_key) > -1"
                class="i-day__table__group">
              <td class="i-day__table__group__td">
                <div class="name">{{ day_set.groups[time_key].name }}</div>
              </td>
              <td class="i-day__table__group__td">
                <div class="count">{{ day_set.groups[time_key].persons }}</div>
                <div class="master">{{ day_set.groups[time_key].masters_string }}</div>
              </td>
            </tr>

            <template v-if="day_set.timing[time_key].deals">

              <!-- Empty cell -->
              <tr v-if="!day_set.timing[time_key].deals.length"
                  @click="dealAdd(day_set, day_set.timing[time_key].label, day_set.timing[time_key].minutes)">
                <td class="i-day__table__td">
                  <div class="day__empty">{{ day_set.timing[time_key].label }}</div>
                </td>
                <td class="day__person"></td>
              </tr>

              <template v-for="(cell_key, deals_index) in day_set.timing[time_key].deals">

                <!-- Empty sub-cell -->
                <tr v-if="day_set.timing[time_key].empty_cells[cell_key]"
                    @click="dealAdd(day_set,
                       day_set.timing[time_key].empty_cells[cell_key].label,
                       day_set.timing[time_key].empty_cells[cell_key].minutes)">
                  <td class="i-day__table__td">
                    <div class="day__empty">{{ day_set.timing[time_key].empty_cells[cell_key].label }}</div>
                  </td>
                  <td class="day__person"></td>
                </tr>

                <!-- Deal -->
                <tr v-if="deals[cell_key]"
                    class="i-schedule__table__deal"
                    @click="dealEdit(deals[cell_key])">

                  <td class="i-day__table__td"
                      :style="{backgroundColor: service.steps[deals[cell_key].step_number].background_color,
                               color: service.steps[deals[cell_key].step_number].color}">
                    <div class="day__deal">
                      <div class="day__deal__time">{{ deals[cell_key].start_string }}</div>
                      <div class="day__deal__minutes" :class="'pravka_'+deals[cell_key].pravka">
                        {{ deals[cell_key].minutes }}
                      </div>
                      <div class="clearfix"></div>
                    </div>
                  </td>

                  <td class="day__person">
                    <div v-if="deals[cell_key].comment" class="day__deal__comment">
                      Комментарий: {{ deals[cell_key].comment }}
                    </div>
                    <div v-for="(person, key_person) in deals[cell_key].persons">
                      <div v-if="key_person === 0 && deals[cell_key].arrear" class="deal_arrear">
                        {{ deals[cell_key].arrear }} руб.
                      </div>
                      <div class="day__person__item">{{ person.string }}</div>
                    </div>
                  </td>

                </tr>

              </template>

            </template>

          </template>

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
        refresh: false,
        loading: true,
        title: 'Расписание на день',
        searching: false,
        service: null,
        service_selected: null,
        service_list: [],
        get_month: null,
        day_set: null,
        deals: {},
      }
    },

    watch: {
      'refresh': function (value, fromValue) {
        if (value === true) {
          this.dayLoad();
        }
      },
      'service_selected': function (value, fromValue) {
        // console.log('watch service', fromValue, ' > ', value);
        this.$store.commit('set_service_id', value);
        this.dayLoad();
      },
    },

    computed: {},

    created() {
    },

    mounted() {
      this.store_subscribe = this.$store.subscribe((mutation, state) => {
        switch (mutation.type) {
          case 'set_refresh_deals':
            this.refresh = state.deal.refresh;
            break;
        }
      });
      document.title = this.title;
      this.serviceLoad();
    },
    beforeDestroy() {
      this.store_subscribe();
    },

    methods: {

      serviceLoad() {
        this.loading = true;
        Vue.axios.get(this.$store.getters.root_url + 'deal/get_service_list/', {params: {'get': true}})
          .then(response => {
            this.service_list = response.data.items;
            if (this.$store.state.deal.service.id) {
              this.service_selected = this.$store.state.deal.service.id;
            } else {
              this.service_selected = this.service_list[0].value;
            }
            this.$store.commit('set_service_id', this.service_selected);
            this.dayLoad();
            this.loading = false;
          })
          .catch(error => {
            alert(error);
          })
          .finally(() => {
            this.loading = false;
          });
      },

      dayLoad(get_day) {
        this.loading = true;
        let params = {
          'day': this.$store.state.deal.day,
          'get_day': get_day,
          'service': this.$store.state.deal.service.id,
        };
        Vue.axios
          .get(this.$store.getters.root_url + 'deal/day/', {params: params})
          .then(response => {
            this.day_set = response.data.day_set;
            this.deals = response.data.deals;
            this.service = response.data.service_set;
            this.$store.commit('set_year', this.day_set.year);
            this.$store.commit('set_month', this.day_set.month);
            this.$store.commit('set_day', this.day_set.key);
          })
          .catch(error => {
            alert(error);
          })
          .finally(() => {
            this.loading = false;
            this.$store.commit('set_refresh_deals', false);
          });
      },

      dealAdd(day, time, minutes) {
        let deal = {
          'service_id': this.service.id,
          'id': 'add',
          'datetime': day.label + ' ' + time,
          'minutes': minutes,
        };
        this.$store.commit('set_deal', deal);
      },
      dealEdit(deal) {
        this.$store.commit('set_deal', deal);
      },

      dayExcel() {
        let url = this.$store.getters.root_url
          + 'deal/day/get_xls?service=' + this.$store.state.deal.service.id
          + '&day=' + this.$store.state.deal.day;
        window.open(url, '_blank');
      },

    }
  }
</script>


<style scoped>

</style>
