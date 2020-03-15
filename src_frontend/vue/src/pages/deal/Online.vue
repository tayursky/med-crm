<template>
  <div class="deal-online">
    <h1>{{ title }}</h1>
    <div v-if="loading" class="loading"></div>

    <div v-if="created">Заявка создана</div>

    <template v-else>
      <div class="deal-content__top">
        <div class="deal-content__top__service_select">
          <el-select v-model="service_selected"
                     filterable
                     placeholder="">
            <el-option v-for="item in service_list"
                       :key="item.value"
                       :label="item.label"
                       :value="item.value">
            </el-option>
          </el-select>
          <el-button icon="el-icon-refresh" @click="serviceLoad"></el-button>
        </div>

        <div class="float-right" v-if="day_set">
          <button v-if="next" type="button" class="el-button" @click="dayLoad('prev')">
            <i class="el-icon-d-arrow-left"></i>
          </button>
          <el-date-picker v-model="day_set.label"
                          class="deal-online__chosen_day"
                          name="day"
                          format="dd.MM.yyyy"
                          value-format="dd.MM.yyyy"
                          :picker-options="picker_options"
                          :clearable=false
                          placeholder=""/>
          <!--<div class="deal-content__top__title">{{ day_set.title }}</div>-->
          <button type="button" class="el-button" @click="dayLoad('next')">
            <i class="el-icon-d-arrow-right"></i>
          </button>
          <el-button icon="el-icon-refresh" class="lime" @click="dayLoad()"></el-button>
        </div>
      </div>

      <div class="clearfix"></div>
      <div class="deal-online__time__help_text">Выберите удобное для приема время</div>
      <div v-if="day_set && timing" class="deal-online__time">
        <template v-for="(time, time_index) in timing">

          <!-- Has deals -->
          <template v-if="day_set.timing[time.key] && day_set.timing[time.key].deals">
            <!-- Empty start -->
            <div v-if="day_set.timing[time.key].empty_start"
                 class="deal-online__time__empty"
                 :class="{'hover': day_set.timing[time.key].empty_start.label === chosen_time}"
                 @click="dealChoseTime(
                 day_set.timing[time.key].empty_start.label,
                 day_set.timing[time.key].empty_start.minutes)">
              {{ day_set.timing[time.key].empty_start.label }} -
              {{ day_set.timing[time.key].empty_start.finish_label }}
            </div>
            <!-- Deal -->
            <div v-for="(deal_key, deal_index) in day_set.timing[time.key].deals"
                 class="deal-online__time__deal"
                 title="Зарезервировано">
              {{ deals[deal_key].start_string }} - {{ deals[deal_key].finish_string }}
            </div>
            <!-- Empty finish -->
            <div v-if="day_set.timing[time.key].empty_finish"
                 class="deal-online__time__empty"
                 :class="{'hover': day_set.timing[time.key].empty_finish.label === chosen_time}"
                 @click="dealChoseTime(
                 day_set.timing[time.key].empty_finish.label,
                 day_set.timing[time.key].empty_finish.minutes)">
              {{ day_set.timing[time.key].empty_finish.label }} -
              {{ day_set.timing[time.key].empty_finish.finish_label }}
            </div>
          </template>

          <!-- Empty -->
          <div v-else-if="day_set.timing_exclude.indexOf(day_set.key+time.key) === -1"
               class="deal-online__time__empty"
               :class="{'hover': time.label === chosen_time}"
               @click="dealChoseTime(time.label, time.minutes)">
            {{ time.label }} - {{ time.finish_label }}
          </div>

        </template>
      </div>

      <div v-if="form && person_set" class="deal-online__form-block">

        <template slot="title">
          <div class="el-dialog__title">
            <div class="el-dialog__title__txt">{{ title }}</div>
          </div>
          <button
              type="button"
              class="el-dialog__headerbtn"
              aria-label="Close"
              v-if=false
              @click="handleClose">
            <i class="el-dialog__close el-icon el-icon-close"></i>
          </button>
        </template>

        <!-- Основной блок сделки -->
        <div v-for="field_name in ordered_fields_filtered"
             class="form-group"
             :class="{'has-errors': field_name in form.errors}">
          <el-row>
            <el-col :span="8"
                    class="form-block__label"
                    :class="{'required_field': form.fields[field_name]['required']}">
              {{ form.fields[field_name].label }}
            </el-col>
            <el-col :span="16">
              <form-field :field_name="field_name"
                          :fields="form.fields"
                          :data="form.data"
                          @changeData="changeData"/>
            </el-col>
            <div v-if="field_name in form.errors" class="form-block__errors">
              <div v-for="error in form.errors[field_name]" class="form-block__errors__item">{{ error }}</div>
            </div>
          </el-row>

          <div v-if="Object.keys(form.errors).length > 0" class="errors-all has-errors form-errors">
            <div v-for="(error, error_key) in form.errors" class="form-errors__item">
              {{ error }}
            </div>
          </div>
        </div>

        <!-- Persons -->
        <div v-if="person_set" class="formset">
          <div class="formset__person_title">
            <div class="formset__person_title__txt">{{ person_set.title }}</div>
            <el-button class="formset__item__add" icon="el-icon-document-add" @click="personAdd()">Добавить</el-button>
          </div>

          <div v-for="(formset_item, formset_index) in person_set.data"
               :key="formset_item+formset_index"
               class="formset__item__row">

            <div v-for="(field_name, index) in person_set.form.ordered_fields"
                 class="row form-group"
                 :key="field_name+index">

              <el-row v-if="!person_set.form.fields[field_name].widget.attrs.hidden"
                      :class="{'has-errors': person_set.formset_errors[formset_index] &&
                    person_set.formset_errors[formset_index][field_name]}">
                <el-col :span="8"
                        class="form-block__label"
                        :class="{'required_field': person_set.form.fields[field_name]['required']}">
                  {{ person_set.form.fields[field_name].label }}
                </el-col>
                <el-col :span="16">
                  <form-field :field_name="field_name"
                              :fields="person_set.form.fields"
                              :data="person_set.data[formset_index]"
                              formset_name="person_set"
                              :formset_index="formset_index"
                              @changeData="personChangeData"/>
                  <div v-if="field_name=='control'" class="help_text">контрольная диагностика после правки</div>
                </el-col>
                <div v-if="person_set.formset_errors[formset_index] &&
                         person_set.formset_errors[formset_index][field_name]"
                     class="form-block__errors">
                  <div v-for="error in person_set.formset_errors[formset_index][field_name]"
                       class="form-block__errors__item">
                    {{ error }}
                  </div>
                </div>
              </el-row>

            </div>

            <el-button class="formset__item__delete" icon="el-icon-delete" @click="personDelete(formset_index)">
              Удалить
            </el-button>
            <div class="clearfix"></div>
          </div>

          <div v-if="Object.keys(person_set.errors).length > 0" class="errors-all has-errors form-errors">
            <div v-for="(error, error_key) in person_set.errors" class="form-errors__item">
              {{ error }}
            </div>
          </div>
        </div>

        <div class="form-block__footer deal-online__form-block__footer">
          <div class="float-right">
            <el-button type="primary" @click="dealSave()">
              <div class="el-button__text">Отправить</div>
            </el-button>
          </div>
          <div class="clearfix"></div>
        </div>

      </div>
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
        loading: true,
        title: '',
        searching: false,
        service: null,
        service_selected: null,
        service_list: [],
        day_set: null,
        deals: {},
        deal: {},
        chosen_time: null,
        chosen_minutes: null,
        minutes: null,
        timing: null,
        picker_options: {firstDayOfWeek: 1},
        form: null,
        form_exclude: ['service', 'service_type', 'step', 'status', 'finish_datetime', 'start_datetime', 'interval'],
        person_set: null,
        next: false,
        created: null,
      }
    },

    watch: {
      'service_selected': function (value, fromValue) {
        // console.log('watch service', fromValue, ' > ', value);
        this.$store.commit('set_service_id', value);
        this.dayLoad();
      },
      'day_set.label'(value, fromValue) {
        this.dayLoad();
      },
      'title'(value, fromValue) {
        document.title = value;
      },
      'person_set.data'(value, fromValue) {
        for (let index in value) {
          this.person_set.data[index].primary = (index === '0');
        }
      },
    },

    computed: {
      ordered_fields_filtered() {
        let answer = [];
        for (let key in this.form.ordered_fields) {
          if (this.form_exclude.indexOf(this.form.ordered_fields[key]) === -1) {
            answer.push(this.form.ordered_fields[key]);
          }
        }
        return answer
      }
    },

    created() {
    },

    mounted() {
      document.title = this.title;
      this.serviceLoad();
    },

    methods: {

      serviceLoad() {
        this.loading = true;
        Vue.axios.get(this.$store.getters.root_url + 'deal/get_service_list/', {params: {'get': true}})
          .then(response => {
            this.service_list = response.data.items;
            this.service_selected = this.service_list[0].value;
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
            this.loading = false;
            console.log(error);
          });
      },

      dayLoad(get_day) {
        this.loading = true;
        this.personClear();
        let params = {
          'get_day': get_day,
          'service': this.$store.state.deal.service.id,
          'day': this.day_set ? this.day_set.label : null,
        };
        Vue.axios.get(this.$store.getters.root_url + 'deal/online/', {params: params})
          .then(response => {
            this.title = response.data.title;
            this.day_set = response.data.day_set;
            this.deals = response.data.deals;
            this.service = response.data.service_set;
            this.timing = response.data.timing;
            this.chosen_time = null;
            this.chosen_minutes = null;
            this.next = response.data.next;
            this.form = response.data.form;
            this.person_set = response.data.person_set;
            this.created = null;
            this.loading = false;
          })
          .catch(error => {
            this.loading = false;
            console.log(error);
          })
      },

      getFormData(object) {
        let formData = new FormData();
        formData.append('csrfmiddlewaretoken', this.form.csrf_token);
        let formset_data = {};
        for (let key in this.formset) {
          formset_data[key] = this.formset[key].data;
        }
        formData.append('formset', JSON.stringify(formset_data));
        Object.keys(object).forEach(
          key => formData.append(key, object[key])
        );
        formData.append('person_set_data', JSON.stringify(this.person_set.data));
        formData.append('service', this.service.id);
        formData.append('start_datetime', this.day_set.label + ' ' + this.chosen_time);
        formData.append('interval', this.chosen_minutes);
        return formData;
      },

      dealSave() {
        this.loading = true;
        Vue.axios.post(this.$store.getters.root_url + 'deal/online/', this.getFormData(this.form.data))
          .then(response => {
            if (response.status === 200 && response.data === 'ok') {
              this.centerDialogVisible = false;
              this.form.errors = {};
              this.person_set.errors = {};
              this.person_set.formset_errors = {};
              this.created = true;
            } else if (response.data.form.errors && response.data.person_set.errors) {
              this.form.errors = response.data.form.errors;
              this.person_set.errors = response.data.person_set.errors;
              this.person_set.formset_errors = response.data.person_set.formset_errors;
            }
            this.loading = false;
          })
          .catch(error => {
            this.loading = false;
            console.log(error);
          })
      },

      dealChoseTime(time, minutes) {
        // console.log('dealChoseTime', time, minutes);
        this.chosen_time = time;
        this.chosen_minutes = minutes;
        this.deal = {
          'service_id': this.service.id,
          'datetime': this.day_set.label + ' ' + time,
          'minutes': minutes,
        };
      },

      changeData(key, value) {
        this.form.data[key] = value;
        // console.log(key, value);
        if (key === 'service_type') {
          for (let key in this.service_types) {
            let type = this.service_types[key];
            if (type.id === value) {
              this.form.data['cost'] = type.cost;
              break;
            }
          }
        }
      },

      personAdd() {
        const new_person = this.clone(this.person_set.form.data);
        this.person_set.data.push(new_person);
      },

      personClear() {
        if (this.person_set) {
          this.person_set.data.splice(0, this.person_set.data.length);
          if (this.person_set.errors.length > 0) {
            this.person_set.errors.splice(0, this.person_set.errors.length);
          }
        }
      },

      personDelete(index) {
        this.person_set.data.splice(index, 1);
        if (this.person_set.errors[index]) {
          this.person_set.errors.splice(index, 1);
        }
      },

      personChangeData(field_name, value, formset_name, formset_index) {
        this.person_set.data[formset_index][field_name] = value;
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


<style scoped>

</style>
