<template>
  <div class="deal-content">

    <deal-dnd></deal-dnd>

    <div v-if="loading" class="loading"></div>
    <div v-else class="i-schedule">

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

        <div v-if="schedule" class="float-right">
          <div class="i-schedule__header__title">
            <el-date-picker class="i-schedule__header__title__picker"
                            v-model="current_day" format="yyyy-MM-dd" value-format="yyyy-MM-dd"
                            :picker-options="{firstDayOfWeek: 1}"/>
            <div class="i-schedule__header__title__text">{{ schedule.title }}</div>
          </div>

          <el-button icon="el-icon-refresh" title="Обновить" @click="scheduleLoad()"/>
        </div>
      </div>

      <div class="i-schedule__filters">
        <div v-for="group in branch_group_services"
             class="i-schedule__filters__item"
             :class="{'selected': branch_group_services_selected.includes(group.id)}"
             @click="filterServiceGroupClick(group.id)">
          {{ group.name }}
        </div>
        <div v-for="master in branch_masters"
             class="i-schedule__filters__item"
             :class="{'selected': branch_masters_selected.includes(master.id)}"
             @click="filterMasterClick(master.id)">
          {{ master.full_name }}
        </div>
      </div>

      <div class="i-schedule__header">
        <router-link tag="button" class="el-button" :to="{name: 'deal_month'}">
          <i class="el-icon-date"></i>Месяц
        </router-link>
        <div class="i-schedule__interval">
          <div class="i-schedule__interval__title">Шаг сетки</div>
          <div v-for="(item, item_index) in intervals.minutes"
               class="i-schedule__interval__item"
               :class="{'selected': item === intervals.current_minutes,
                        'last': intervals.days.length-1 === item_index}"
               @click="setInterval('minutes', item)">
            {{ item }}
          </div>

          <div class="i-schedule__interval__title">Дней</div>
          <div v-for="(item, item_index) in intervals.days"
               class="i-schedule__interval__item"
               :class="{'selected': item === intervals.current_days,
                        'last': intervals.days.length-1 === item_index}"
               @click="setInterval('days', item)">
            {{ item }}
          </div>

          <button class="el-button i-schedule__table__deal_details_icon"
                  :class="{'i-schedule__table__deal_details_icon__true': deals_details_show}"
                  type="button"
                  title="Детализация сделок"
                  @click="deals_details_show = !deals_details_show">
            <i class="el-icon-view"></i>
          </button>
        </div>

        <div class="float-right">
          <el-button-group>
            <button type="button" class="el-button el-button--plain el-button--mini" @click="scheduleLoad('current')">
              Сегодня
            </button>
            <button type="button" class="el-button" title="Предыдущая неделя" @click="scheduleLoad('prev')">
              <i class="el-icon-d-arrow-left"></i>
            </button>
            <button type="button" class="el-button" title="Следующая неделя" @click="scheduleLoad('next')">
              <i class="el-icon-d-arrow-right"></i>
            </button>
          </el-button-group>
        </div>
        <div class="clearfix"></div>
      </div>

      <table cellspacing="0" cellpadding="0" class="i-schedule__table">
        <thead>
        <th v-for="(day, day_index) in schedule.days"
            class="i-schedule__table__head__th"
            :class="{'i-schedule__table__head__th__today': schedule.today === day.iso}"
            :colspan="day.masters.length"
            @click="goDay(day.iso)">
          <div class="i-schedule__table__head__weekday_label">{{ day.weekday_label }}</div>
          <div class="i-schedule__table__head__day">{{ parseInt(day.iso.slice(-2)) }}</div>
        </th>
        </thead>

        <tbody>
        <tr>
          <template v-for="(day, day_index) in schedule.days">
            <td v-if="day.masters.length === 0" class="i-schedule__table__head__master"></td>
            <td v-for="master in day.masters" class="i-schedule__table__head__master">
              <div class="i-schedule__table__head__full_name">{{ master.last_name }}</div>
              <div class="i-schedule__table__head__print" @click="getExcel(day, master)"><i
                  class="el-icon-document"></i></div>
            </td>
          </template>
        </tr>

        <tr v-for="(range, range_index) in schedule_range">

          <template v-for="(day, day_index) in schedule.days">

            <td v-if="day.masters.length === 0" class="i-schedule__table__cell"></td>
            <td v-for="master in day.masters" class="i-schedule__table__cell">
              <div class="i-schedule__table__call_wrap">

                <template v-for="(group, group_index) in getTimeGroup(day, master, range)">
                  <template v-if="group.timeout && groups_timeout_show">
                    <div class="i-schedule__table__timeout"
                         :style="{top: group.top+'px', height: group.interval*cell_height-2+'px'}">
                      <div class="i-schedule__table__timeout__title">
                        <div class="i-schedule__table__timeout__close"
                             @click="groups_timeout_show = !groups_timeout_show"></div>
                        <div class="i-schedule__table__timeout__item" :style="{lineHeight: cell_height-1+'px'}">
                          {{ $moment(group.start).format("HH:mm") }} -
                        </div>
                        <div class="i-schedule__table__timeout__item" :style="{lineHeight: cell_height-1+'px'}">
                          {{ $moment(group.end).format("HH:mm") }}
                        </div>
                        <div class="i-schedule__table__timeout__item"
                             :style="{lineHeight: cell_height-1+'px', display: 'block'}">
                          {{ group.name }}
                        </div>
                      </div>
                    </div>
                  </template>
                  <template v-else>
                    <div class="i-schedule__table__time_group" :style="{top: group.top+'px'}"
                         :title="group.name + ' | ' + group.persons_count">
                      <div class="i-schedule__table__time_group__help"></div>
                    </div>
                    <div class="i-schedule__table__time_group__top" :style="{top: group.top+'px'}"></div>
                    <div class="i-schedule__table__time_group__bottom"
                         :style="{top: group.top+group.interval*cell_height-3+'px'}"></div>
                    <div class="i-schedule__table__time_group__right"
                         :style="{top: group.top+2+'px', height: group.interval*cell_height-4+'px'}"></div>
                    <div class="i-schedule__table__time_group__left"
                         :style="{top: group.top+'px', height: group.interval*cell_height-2+'px'}"></div>
                  </template>
                </template>

                <template v-for="item in getDeals(day, master, range)">

                  <!-- Deal -->
                  <div v-if="item.id" class="i-schedule__table__deal"
                       :class="{'i-schedule__table__deal_short': deals_details_show}"
                       :style="{top: item.top+'px',
                                height: cell_height*item.interval-2+'px',
                                backgroundColor: stages[item.stage].background_color,
                                color: stages[item.stage].color}"
                       @click="dealEdit(item)">
                    <drag :transfer-data="item.id"
                          @dragstart="dndDrag(item, master)">
                      <div class="i-schedule__table__deal__body">
                        <div class="i-schedule__table__deal__time">
                          {{ $moment(item.start_iso).format("HH:mm") }} - {{ $moment(item.end_iso).format("HH:mm") }}
                        </div>
                        <div v-if="!deals_details_show" class="i-schedule__table__deal__persons">
                          <div v-for="person in item.persons"
                               class="i-schedule__table__deal__person">
                            {{ person.cache.full_name }}
                          </div>
                        </div>
                      </div>
                      <div class="i-schedule__table__deal__persons_count"
                           :class="'pravka_'+item.pravka"
                           :style="{height: cell_height*item.interval+'px'}">
                        {{ item.persons.length }}
                      </div>
                    </drag>
                  </div>
                  <div v-if="item.id && deals_details_show"
                       class="i-schedule__table__deal_details"
                       :style="{top: item.top+'px',
                                height: cell_height*item.interval-1+'px'}">
                    <div v-if="item.cost - item.paid !== 0 || item.comment">
                      <span v-if="item.cost - item.paid !== 0" class="i-schedule__table__deal_details__debt">
                        {{ item.cost - item.paid }} р.
                      </span>
                      <span v-if="item.comment" class="i-schedule__table__deal_details__comment">
                        {{ item.comment }}
                      </span>
                    </div>
                    <div v-for="person in item.persons" class="i-schedule__table__deal_details__person">
                      <div class="i-schedule__table__deal_details__person__full_name">{{ person.cache.full_name }}</div>
                      <div class="i-schedule__table__deal_details__person__age">{{ person.cache.age }}</div>
                    </div>
                  </div>

                  <!-- Empty -->
                  <div v-else class="i-schedule__table__empty"
                       :class="{'over': master.id === $store.state.deal.drag_drop.master &&
                       $moment(item.start).format().slice(0, 16) === $store.state.deal.drag_drop.start_iso}"
                       :style="{top: item.top+'px', height: cell_height*item.interval-1+'px'}"
                       :title="$moment(item.start).format('HH:mm') + ' - ' + $moment(item.end).format('HH:mm')"
                       @click="dealAdd(cellRaise(day, item), master)">
                    <drop class="i-schedule__table__empty__time"
                          @dragenter="dndEnter(cellRaise(day, item), master)"
                          @dragleave="dndLeave"
                          @drop="dndDrop">
                    </drop>
                  </div>
                </template>

                <template v-for="(item, item_index) in cellEmpty(day, master, range)">
                  <div class="i-schedule__table__height"
                       :class="{'over': master.id === $store.state.deal.drag_drop.master &&
                                 day.iso + 'T' + item.start_time === $store.state.deal.drag_drop.start_iso,
                                'inner-border-top': item.top > 0}"
                       :style="{top: item.top+'px', height: cell_height*item.interval-1+'px'}"
                       :title="item.start_time + ' - ' + item.end_time"
                       @click="dealAdd(cellRaise(day, item), master)">
                    <drop class="i-schedule__table__cell_time"
                          @dragenter="dndEnter(cellRaise(day, item), master)"
                          @dragleave="dndLeave"
                          @drop="dndDrop">
                      {{ item.start_time }}
                    </drop>
                  </div>
                </template>

              </div>
            </td>
          </template>

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
  import {Drag, Drop} from 'vue-drag-drop';
  import DealDnd from './DealDnd';

  Vue.use(VueAxios, axios);

  export default {
    components: {DealDnd, Drag, Drop},
    data() {
      return {
        select_all: true,
        select_all_switch: false,
        cell_height: 24,
        intervals: {
          'minutes': [5, 10, 15, 20, 30], 'current_minutes': 15,
          'days': [1, 2, 3, 5, 7], 'current_days': 7,
        },
        current_day: null,
        refresh: false,
        loading: true,
        branch: {id: null, group_services: []},
        branch_set: {group_services: []},
        branch_group_services_selected: [],
        branch_masters_selected: [],
        stages: [],
        schedule: {},
        groups_timeout_show: true,
        deals: {},
        deals_details_show: false,
        over: false
      }
    },

    watch: {
      'current_day'(value, fromValue) {
        if (value) {
          this.$store.commit('set_current_day', value);
          this.scheduleLoad();
        }
      },
      'refresh'(value, fromValue) {
        if (value === true) {
          this.scheduleLoad();
        }
      },

      'intervals.current_days'(value, fromValue) {
        this.deals_details_show = value === 1;
        this.scheduleLoad();
      },

      'branch': {
        handler: function (branch, fromValue) {
          this.select_all_switch = this.select_all;
          this.branch_group_services_selected = [];
          this.branch_masters_selected = [];
          if (branch.id) {
            this.$store.commit('set_branch', {'id': branch.id});
          } else {
            this.$store.commit('set_branch', {'id': null});
          }
          this.scheduleLoad();
        },
        deep: true
      },
      'schedule': {
        handler: function (branch, fromValue) {
          this.groups_timeout_show = true;
        },
        deep: true
      },
    },

    computed: {
      branch_group_services() {
        let group_services = [];
        for (let group_id in this.branch_set.group_services) {
          if (this.branch.group_services.includes(parseInt(group_id))) {
            group_services.push({
              id: parseInt(group_id),
              name: this.branch_set.group_services[group_id].name
            });
            if (this.select_all_switch) {
              this.branch_group_services_selected.push(parseInt(group_id));
            }
          }
        }
        let unselect_masters = [];
        for (let key in this.branch_masters_selected) {
          let master = this.branch_set['masters'][this.branch_masters_selected[key]];
          if (!this.branch_masters.includes(master)) {
            unselect_masters.push(master['id']);
          }
        }
        for (let key in unselect_masters) {
          this.branch_masters_selected.splice(this.branch_masters_selected.indexOf(unselect_masters[key]), 1);
        }
        return group_services
      },

      branch_masters() {
        let masters = [];
        for (let key in this.branch_group_services_selected) {
          let group_id = this.branch_group_services_selected[key];
          for (let master_id in this.branch_set.masters) {
            let master = this.branch_set.masters[master_id];
            if (master.group_services.includes(parseInt(group_id)) && !masters.includes(master)) {
              masters.push(master);
            }
          }
        }
        if (this.select_all_switch) {
          this.select_all_switch = false;
          for (let key in masters) this.branch_masters_selected.push(masters[key]['id']);
        }
        return masters
      },

      schedule_range() {
        let range = [];
        let start = new Date(this.schedule.start_iso + 'T' + this.schedule.range.start);
        let end = new Date(this.schedule.start_iso + 'T' + this.schedule.range.end);
        while (start < end) {
          let item = {
            'start_time': this.$moment(start).format('HH:mm')
          };
          start = new Date(start.getTime() + this.intervals.current_minutes * 60000);
          item['end_time'] = this.$moment(start).format('HH:mm');
          range.push(item);
        }
        return range
      },

      cell_height_relation() {
        return this.cell_height / this.intervals.current_minutes
      }
    },

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
      document.title = 'Расписание на неделю';
      this.branchLoad();
    },

    beforeDestroy() {
      this.store_subscribe();
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
            this.scheduleLoad();
          });
      },

      scheduleLoad(step) {
        this.loading = true;
        let params = {
          'branch': this.branch.id,
          'current_day': this.$store.state.deal.current_day,
          'days': this.intervals.current_days,
          'step': step || null,
          'masters': JSON.stringify(this.branch_masters_selected),
        };
        Vue.axios
          .get(this.$store.getters.root_url + 'deal/schedule/', {params: params})
          .then(response => {
            this.current_day = response.data.current_day;
            this.stages = response.data.stages;
            this.deals = response.data.deals;
            this.schedule = response.data.schedule;
          })
          .catch(error => {
            console.log(error);
          })
          .finally(() => {
            this.$store.commit('set_refresh_deals', false);
            this.loading = false;
          });
      },

      filterServiceGroupClick(group_id) {
        if (this.branch_group_services_selected.includes(group_id)) {
          this.branch_group_services_selected.splice(this.branch_group_services_selected.indexOf(group_id), 1);
        } else {
          this.branch_group_services_selected.push(group_id);
        }
      },

      filterMasterClick(master_id) {
        if (this.branch_masters_selected.includes(master_id)) {
          this.branch_masters_selected.splice(this.branch_masters_selected.indexOf(master_id), 1);
        } else {
          this.branch_masters_selected.push(master_id);
        }
      },

      setInterval(type, value) {
        if (type === 'minutes') this.intervals.current_minutes = value;
        else if (type === 'days') this.intervals.current_days = value;
      },

      cellEmpty(day, master, range) {
        let cell_start = new Date(day['iso'] + 'T' + range['start_time']);
        let cell_end = new Date(day['iso'] + 'T' + range['end_time']);
        let master_start_time = new Date(master['plan_start_iso']);
        let master_end_time = new Date(master['plan_end_iso']);
        if (
          cell_start >= master_start_time && cell_start < master_end_time &&
          cell_end > master_start_time && cell_end <= master_end_time) {
          return [{
            'top': 0,
            'interval': 1,
            'start_time': range['start_time'],
            'end_time': range['end_time']
          }]
        } else if (
          cell_start < master_start_time && cell_start < master_end_time &&
          cell_end > master_start_time && cell_end < master_end_time) {
          return [{
            'top': (master_start_time - cell_start) / 60000 * this.cell_height_relation,
            'interval': (cell_end - master_start_time) / 60000 / this.intervals.current_minutes,
            'start_time': this.$moment(master_start_time).format().slice(11, 16),
            'end_time': range['end_time']
          }];
        } else if (
          cell_start > master_start_time && cell_start < master_end_time &&
          cell_end > master_start_time && cell_end > master_end_time) {
          return [{
            'top': 0,
            'interval': (master_end_time - cell_start) / 60000 / this.intervals.current_minutes,
            'start_time': range['start_time'],
            'end_time': this.$moment(master_end_time).format().slice(11, 16)
          }];
        }
      },

      getTimeGroup(day, master, cell) {
        let groups = [];
        let cell_start_day = new Date(day['iso']);
        let cell_start = new Date(day['iso'] + 'T' + cell['start_time']);
        let cell_end = new Date(day['iso'] + 'T' + cell['end_time']);

        for (let index in this.schedule.time_groups) {
          let item = this.schedule.time_groups[index];
          let item_start_day = new Date(item['start_date']);
          let item_end_day = new Date(item['end_date']);
          let item_start = new Date(day['iso'] + 'T' + item['start_time']);
          // console.log(day['iso'] + ' ' + cell['start_time'], index,
          //   (item_start_day <= cell_start_day && cell_start_day <= item_end_day) &&
          //   (cell_start <= item_start && item_start < cell_end));
          if (item_start_day <= cell_start_day && cell_start_day <= item_end_day &&
            cell_start <= item_start && item_start < cell_end && item.users.includes(master.id)) {
            let start = new Date(day['iso'] + 'T' + item['start_time']);
            let end = new Date(day['iso'] + 'T' + item['end_time']);

            let persons_count = 0;
            for (let deal_index in this.deals) {
              let _deal = this.deals[deal_index];
              _deal['start'] = new Date(_deal['start_iso']);
              _deal['end'] = new Date(_deal['end_iso']);
              if(master['id'] === _deal['master'] && (start <= _deal['start'] && _deal['end'] <= end)){
                persons_count += _deal['persons'].length;
              }
            }

            groups.push({
              'id': item.id,
              'name': item.name,
              'timeout': item.timeout,
              'master': master.id,
              'top': (start - cell_start) / 60000 * this.cell_height_relation,
              'start': start,
              'end': end,
              'interval': (end - start) / 60000 / this.intervals.current_minutes,
              'show': true,
              'persons_count': persons_count
            });
            // console.log('time_groups', day['iso'], item['start_time'], item['end_time']);
          }
        }
        return groups
      },

      getDeals(day, master, cell) {
        // Deals and timeouts
        let cell_list = [];
        let cell_start = new Date(day['iso'] + 'T' + cell['start_time']);
        let cell_end = new Date(day['iso'] + 'T' + cell['end_time']);
        let step_datetime = cell_start;

        if (!master) return cell_list;

        for (let index in this.deals) {
          let deal = this.deals[index];
          deal['start'] = new Date(deal['start_iso']);
          deal['end'] = new Date(deal['end_iso']);
          if (deal['master'] === master['id'] && (deal['start'] >= cell_start && deal['start'] < cell_end)) {

            if (step_datetime < deal['start']) {
              cell_list.push({
                'master': true,
                'top': (step_datetime - cell_start) / 60000 * this.cell_height_relation,
                'start': step_datetime,
                'end': deal['start'],
                'interval': (deal['start'] - step_datetime) / 60000 / this.intervals.current_minutes
              });
            }
            deal['top'] = (deal['start'] - cell_start) / 60000 * this.cell_height_relation;
            deal['interval'] = (deal['end'] - deal['start']) / 60000 / this.intervals.current_minutes;
            cell_list.push(this.deals[index]);
            step_datetime = deal['end'];
          }
        }
        let deal = cell_list[cell_list.length - 1];
        if (deal) {
          if (deal['end'] < cell_end) {
            cell_list.push({
              'top': (deal['end'] - cell_start) / 60000 * this.cell_height_relation,
              'start': deal['end'],
              'end': cell_end,
              'interval': (cell_end - deal['end']) / 60000 / this.intervals.current_minutes
            });
          }
        } else {
          let check_big_deals = this.deals.filter(function (_deal) {
            return _deal['end'] > cell_start && _deal['end'] < cell_end
          });
          if (check_big_deals.length > 0) {
            let _deal = check_big_deals[0];
            cell_list.push({
              'top': (_deal['end'] - cell_start) / 60000 * this.cell_height_relation,
              'start': _deal['end'],
              'end': cell_end,
              'interval': (cell_end - _deal['end']) / 60000 / this.intervals.current_minutes
            });
          }
        }
        return cell_list
      },

      cellRaise(day, item) {
        let data = {};
        if (item['start_time'] && item['end_time']) {
          data['start_iso'] = day['iso'] + 'T' + item['start_time'];
          data['end_iso'] = day['iso'] + 'T' + item['end_time'];
        } else if (item['start'] && item['end']) {
          data['start_iso'] = this.$moment(item['start']).format().slice(0, 16);
          data['end_iso'] = this.$moment(item['end']).format().slice(0, 16);
        }
        return data
      },

      dealAdd(item, master) {
        let deal = {
          'id': 'add',
          'start_iso': item['start_iso'],
          'end_iso': item['end_iso'],
        };
        if (master) deal['master'] = master.id;
        this.$store.commit('set_deal', deal);
      },

      dealEdit(deal) {
        this.$store.commit('set_deal', deal);
      },

      goDay(day) {
        this.current_day = day;
        this.intervals.current_days = 1;
      },

      dndDrag(deal, master) {
        console.log('dndDrag');
        console.log(deal);
        let _deal = {id: deal.id, minutes: deal.minutes, master: master};
        this.$store.commit('set_drag_drop', _deal);
      },
      dndEnter(data, master) {
        data['master'] = master;
        this.$store.commit('update_drag_drop', data);
      },
      dndLeave() {
        this.$store.commit('update_drag_drop', {});
      },
      dndDrop(data) {
        this.$store.commit('update_drag_drop', {drop: true});
        this.$store.commit('set_deal', {id: this.$store.state.deal.drag_drop.id});
      },

      getExcel(day, master) {
        let url = this.$store.getters.root_url
          + 'deal/schedule/xls?branch=' + this.branch.id
          + '&current_day=' + day.iso
          + '&masters=[' + master.id + ']'
          + '&days=1';
        window.open(url, '_blank');
      }

    }
  }
</script>


<style scoped>
  .over {
    background: #ccc;
  }
</style>
