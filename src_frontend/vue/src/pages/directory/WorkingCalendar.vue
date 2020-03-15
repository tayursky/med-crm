<template>

  <div class="directory working_calendar">
    <div v-if="loading" class="loading"></div>

    <template v-else-if="calendar_set.year">
      <el-row class="directory__head">
        <div class="directory__title">{{ title }}</div>
        <div class="directory__buttons">

          <button v-if="permissions.indexOf('add') > -1"
                  type="button"
                  class="el-button el-button--plain el-button--mini margin-right-10"
                  @click="yearLoad('parse')">
            <div class="text">Парсить</div>
          </button>

          <el-button-group>
            <button type="button" class="el-button el-button--plain el-button--mini" @click="yearLoad('current')">
              <div class="text">Текущий год</div>
            </button>
            <button type="button" class="el-button" title="Предыдущий год" @click="yearLoad('prev')">
              <i class="el-icon-d-arrow-left"></i>
            </button>
            <button type="button" class="el-button" title="Следующий год" @click="yearLoad('next')">
              <i class="el-icon-d-arrow-right"></i>
            </button>
          </el-button-group>

          <div class="deal-content__top__title">{{ calendar_set.year }}</div>
          <el-button icon="el-icon-refresh" title="Обновить" @click="yearLoad()"/>
        </div>
      </el-row>

      <div v-if="calendar_set.months.length === 0"
           class="working_calendar__empty">
        Нет данных
      </div>

      <template v-else>
        <div class="working_calendar__annotate">
          <div class="workdays">{{ calendar_set.annotate.workdays + calendar_set.annotate.pre_holidays }}</div>
          рабочих дней, в том числе
          <div class="pre_holidays">{{ calendar_set.annotate.pre_holidays }}</div>
          сокращенных дней,
          <div class="holidays">{{ calendar_set.annotate.holidays }}</div>
          праздничных дней,
          <div class="weekends">{{ calendar_set.annotate.weekends }}</div>
          выходных
        </div>

        <div class="working_calendar__months">
          <template v-for="(month, month_index) in calendar_set.months">

            <table class="working_calendar__month">
              <thead>
              <tr>
                <th class="working_calendar__month__label" colspan="7">{{ month.label }}</th>
              </tr>
              <tr>
                <th class="working_calendar__month__annotate" colspan="7">
                  {{ month.annotate.workdays + month.annotate.pre_holidays }} рабочих дней,
                  {{ month.annotate.hours }} часов
                </th>
              </tr>
              </thead>

              <tbody>
              <tr v-for="(week, week_index) in month.weeks">
                <template v-for="(day, day_index) in getWeek(week, month.days)">
                  <td v-if="day_index === 0 && day.weekday > 0" :colspan="day.weekday"></td>
                  <td class="working_calendar__day"
                      :class="day.day_type">
                    {{ day.day }}
                  </td>
                </template>
              </tr>
              </tbody>
            </table>

          </template>
        </div>
      </template>
    </template>

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
        title: '',
        loading: true,
        searching: false,
        get_month: null,
        calendar_set: {},
        permissions: []
      }
    },

    watch: {},

    computed: {},

    created() {
    },

    mounted() {
      document.title = 'Календарь на месяц';
      this.yearLoad();
    },

    methods: {

      getWeek(week, days) {

        return days.filter(function (day) {
          return day.week === week
        })
      },

      yearLoad(action) {
        this.loading = true;
        let params = {
          'get': 'working_calendar',
          'action': action
        };
        if (this.calendar_set.year) {
          params['year'] = parseInt(this.calendar_set.year);
        }
        Vue.axios.get(this.$store.getters.root_url + 'directory/working_calendar/', {params: params})
          .then(response => {
            this.title = response.data.title;
            this.calendar_set = response.data.calendar_set;
            this.permissions = response.data.permissions;
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
        console.log('goWeek', day);
        this.$store.commit('set_day', day);
        this.$router.push({name: 'schedule'});
      },

      goDay(day) {
        console.log('goDay', day);
        this.$store.commit('set_day', day);
        this.$router.push({name: 'deal_day'});
      },
    }
  }
</script>


<style scoped>

</style>
