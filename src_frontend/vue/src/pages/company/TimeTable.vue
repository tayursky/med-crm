<template>
  <div>
    <div class="loading" v-if="loading"></div>
    <div v-else class="directory company-timetable">
      <div class="company-timetable__header">

        <filters :filters="filters" @refresh="monthLoad" @changeFilters="filtersChange"/>

        <div class="directory__buttons">
          <div class="deal-content__top__title" v-if="month_set">{{ month_set.year }} {{ month_set.month_name }}</div>
          <el-button icon="el-icon-refresh" title="Обновить" @click="monthLoad()"/>
        </div>
        <div class="clearfix"></div>
      </div>

      <template v-if="month_set">
        <div class="i-month__header">
          <template v-if="permissions.includes('change')">
            <div class="company-timetable__time">
              <el-time-picker v-model="start_time" name="start_time" format="HH:mm" value-format="HH:mm"/>
              <el-time-picker v-model="end_time" name="end_time" format="HH:mm" value-format="HH:mm"/>
            </div>
            <el-button-group>
              <button type="button" class="el-button" :class="{'selected': selection}" @click="daySelection()">
                <template v-if="!selection">
                  <i class="el-icon-magic-stick"></i><span>Выбрать</span>
                </template>
                <template v-else>
                  <i class="el-icon-close"></i><span>Отмена</span>
                </template>
              </button>
              <button v-if="selection" type="button" title="Удалить"
                      class="el-button" :class="{'selected': selection}" @click="daySelectionSet('delete')">
                <i class="el-icon-delete"></i>
              </button>
              <button v-if="selection" type="button" title="Сохранить"
                      class="el-button" :class="{'selected': selection}" @click="daySelectionSet('change')">
                <i class="el-icon-check"></i>
              </button>
            </el-button-group>
          </template>

          <div class="float-right">
            <el-button-group>
              <button type="button" class="el-button" @click="monthLoad('current')">
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
      </template>

      <table v-if="month_set" class="company-timetable__table">
        <thead>
        <tr>
          <td class="company-timetable__thead__user" rowspan="2">Ф.И.О.</td>
          <td v-for="(day, day_index) in month_set.days"
              class="company-timetable__thead__th"
              :class="{'company-timetable__tbody__day_focus': day.day === day_focus}"
              @mouseover="dayOver(day)" @mouseleave="dayLeave"
              @click="dayClick(day)">
            {{ month_set.week_heads[day.weekday] }}
          </td>
          <td class="company-timetable__thead__th" colspan="2">План</td>
          <td class="company-timetable__thead__th" colspan="2">Фактич.</td>
        </tr>
        <tr>
          <td v-for="(day, day_index) in month_set.days"
              class="company-timetable__thead__th"
              :class="{'company-timetable__tbody__day_focus': day.day === day_focus}"
              @mouseover="dayOver(day)" @mouseleave="dayLeave"
              @click="dayClick(day)">
            {{ day.day }}
          </td>
          <td class="company-timetable__thead__th" title="Смен"><i class="el-icon-notebook-2"></i></td>
          <td class="company-timetable__thead__th" title="Часов"><i class="el-icon-time"></i></td>
          <td class="company-timetable__thead__th" title="Смен"><i class="el-icon-notebook-2"></i></td>
          <td class="company-timetable__thead__th" title="Часов"><i class="el-icon-time"></i></td>
        </tr>
        </thead>

        <tbody>
        <tr v-for="(user_id, user_key) in workers.users_ordered" class="company-timetable__tbody__tr">
          <td class="company-timetable__tbody__user" @click="userClick(user_id)">
            {{ workers.users[user_id].short_name }}
          </td>
          <td v-for="(day, day_index) in month_set.days"
              class="company-timetable__tbody__day"
              :class="[day.day === day_focus ? 'company-timetable__tbody__day_focus' : '',
                         selection_array[user_id] && selection_array[user_id].includes(day.iso) ? 'selected' : '']"
              @mouseover="dayOver(day)"
              @mouseleave="dayLeave">

            <div v-if="work_shifts[day.iso] && work_shifts[day.iso][user_id]"
                 class="company-timetable__tbody__shift"
                 @click="shiftClick(day, user_id, work_shifts[day.iso][user_id].id)">
              {{ work_shifts[day.iso][user_id].time_int }}
            </div>
            <div v-else
                 class="company-timetable__tbody__shift"
                 @click="dayClick(day, user_id)">
            </div>

          </td>
          <td class="company-timetable__tbody__day">
            <div class="company-timetable__tbody__shift">{{ workers.users[user_id].shifts }}</div>
          </td>
          <td class="company-timetable__tbody__day">
            <div class="company-timetable__tbody__shift">{{ workers.users[user_id].hours }}</div>
          </td>
          <td class="company-timetable__tbody__day">
            <div class="company-timetable__tbody__shift"></div>
          </td>
          <td class="company-timetable__tbody__day">
            <div class="company-timetable__tbody__shift"></div>
          </td>
        </tr>

        <tr class="time_groups__hr">
          <td :colspan="month_set.days[month_set.days.length-1]['day'] + 5"></td>
        </tr>
        <tr class="time_groups">
          <td class="time_groups__title">Группы</td>
          <td v-for="(day, day_index) in month_set.days"
              class="time_groups__day"
              @click="groupEdit({'id': 'add',
              'initial': {'branch': $store.state.deal.branch.id, 'start_date': day.iso,
              'end_date': day.iso}})">
            {{ day.day }}
          </td>
          <td :colspan="month_set.days[month_set.days.length-1]['day'] + 4"></td>
        </tr>

        <tr v-for="(group, group_index) in time_groups" class="time_groups__item" @click="groupEdit(group)">
          <td :colspan="group.start_date.substr(-2)" class="time_groups__name">{{ group.name }}</td>
          <td :colspan="group.end_date.substr(-2) - group.start_date.substr(-2) + 1" class="time_groups__day">
            <div class="time_groups__day__group" :class="{'time_groups__day__timeout': group.timeout}"></div>
          </td>
          <td :colspan="month_set.days[month_set.days.length-1]['day'] - group.end_date.substr(-2) + 5"
              class="time_groups__time">
            {{ group.start_time }} - {{ group.end_time }}
          </td>
        </tr>
        </tbody>
      </table>

    </div>

    <the-dialog app_label="company"
                model_name="timetable"
                :item="item"
                :permissions="permissions"
                @itemClose="itemClose"/>

    <the-dialog app_label="company"
                model_name="timegroup"
                :item="time_group"
                :permissions="permissions"
                @itemClose="groupClose"/>

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
        loading: false,
        title: '',
        month_set: null,
        workers: null,
        work_shifts: null,
        day_focus: null,
        selection: false,
        selection_array: {},
        start_time: null,
        end_time: null,
        permissions: [],
        filters: null,
        time_groups: [],
        time_group: {},
        item: {},
      }
    },

    watch: {
      'branch.id': function (value, fromValue) {
        this.$store.commit('set_branch', {'id': value});
        this.monthLoad();
      },
      'title'(value, fromValue) {
        document.title = value;
      },
    },

    computed: {},

    created() {
    },

    mounted() {
      this.monthLoad();
    },

    methods: {

      monthLoad(get_month) {
        this.loading = true;
        let params = {
          'get': true,
          'get_month': get_month,
          'branch': this.$store.state.deal.branch.id,
          'current_day': this.$store.state.deal.current_day,
        };
        if (this.filters) {
          for (let filter_key in this.filters.data) {
            params[filter_key] = this.filters.data[filter_key];
          }
        }
        Vue.axios
          .get(this.$store.getters.root_url + 'company/timetable/', {params: params})
          .then(response => {
            this.title = response.data.title;
            this.month_set = response.data.month_set;
            this.workers = response.data.workers;
            this.work_shifts = response.data.work_shifts;
            this.start_time = response.data.start_time;
            this.end_time = response.data.end_time;
            this.permissions = response.data.permissions;
            this.filters = response.data.filters;
            this.time_groups = response.data.time_groups;
            this.$store.commit('set_branch', {'id': response.data.branch});
            this.$store.commit('set_current_day', response.data.current_day);
          })
          .catch(error => {
            console.log(error);
          })
          .finally(() => {
            this.selection = false;
            this.selection_array = {};
            this.loading = false;
          });
      },
      dayOver(day) {
        this.day_focus = day.day;
      },
      dayLeave() {
        this.day_focus = null;
      },
      daySelection() {
        this.selection = !this.selection;
        if (!this.selection) this.selection_array = {};
      },

      daySelectionSet(action) {
        this.loading = true;
        let formData = new FormData();
        formData.append('shift_set', JSON.stringify(this.selection_array));
        formData.append('start_time', JSON.stringify(this.start_time));
        formData.append('end_time', JSON.stringify(this.end_time));

        Vue.axios
          .post(this.$store.getters.root_url + 'company/timetable/set/' + action + '/', formData)
          .then(response => {
            this.title = response.data.title;
          })
          .catch(error => {
            console.log(error);
          })
          .finally(() => {
            this.monthLoad();
          });
      },

      dayClick(day, user_id) {
        this.day_focus = null;
        console.log('dayClick', day.iso, user_id);
        if (this.selection) {
          if (user_id) {
            if (!this.selection_array[user_id]) {
              this.selection_array[user_id] = [];
            }
            if (this.selection_array[user_id].includes(day.iso)) {
              this.selection_array[user_id].splice(this.selection_array[user_id].indexOf(day.iso), 1);
            } else {
              this.selection_array[user_id].push(day.iso);
            }
          } else {
            // Выделение дня для всех сотрудников
            for (let key in this.workers.users_ordered) {
              user_id = this.workers.users_ordered[key];
              if (!this.selection_array[user_id]) {
                this.selection_array[user_id] = [];
              }
              if (this.selection_array[user_id].includes(day.iso)) {
                this.selection_array[user_id].splice(this.selection_array[user_id].indexOf(day.iso), 1);
              } else {
                this.selection_array[user_id].push(day.iso);
              }
            }
          }
          console.log(this.selection_array);
        } else if (day && user_id) {
          this.item = {
            'id': 'add',
            'initial': {
              'branch': this.filters.data.branch,
              'user': user_id,
              'plan_start_datetime': day.iso + 'T' + this.start_time,
              'plan_end_datetime': day.iso + 'T' + this.end_time,
            }
          };
        }

        this.day_focus = day.day;
      },

      userClick(user_id) {
        if (this.selection) {

          if (!this.selection_array[user_id]) {
            this.selection_array[user_id] = [];
          }
          for (let day_key in this.month_set.days) {
            let day = this.month_set.days[day_key];
            if (this.selection_array[user_id].includes(day.key)) {
              this.selection_array[user_id].splice(this.selection_array[user_id].indexOf(day.key), 1);
            } else {
              this.selection_array[user_id].push(day.key);
            }
            this.day_focus = day.key;
          }
          this.day_focus = null;
        }
      },

      shiftClick(day, user_id, id) {
        if (this.selection) {
          this.dayClick(day, user_id);
        } else {
          this.item = {'id': id};
        }
      },

      filtersChange(key, value) {
        this.filters.data[key] = value;
        this.monthLoad();
      },

      filterReset() {
        for (let key in this.filters.data) {
          this.filters.data[key] = '';
        }
        this.monthLoad();
      },

      itemClose(reload = true) {
        this.item = {};
        if (reload) {
          this.monthLoad();
        }
      },

      formsetChangeData() {

      },

      groupEdit(time_group) {
        console.log('groupEdit', time_group);
        this.time_group = time_group;
      },
      groupClose(reload = true) {
        this.time_group = {};
        if (reload) {
          this.monthLoad();
        }
      }

    }
  }
</script>


<style scoped>

</style>
