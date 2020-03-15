<template>
  <div>
    <div v-if="loading" class="modal-loading"></div>
    <div v-else-if="deal.id && form" class="el-tabs__form">

      <div v-if="!hide_title" class="form_tab__title">{{ title }}</div>

      <deal-form-stage :stages="stages" :current_stage_id="form.data.stage" @changeData="changeData"/>

      <div v-for="field_name in ordered_fields_filtered"
           class="form-group" :class="{'has-errors': field_name in form.errors}">

        <el-row v-if="field_name === 'cost'">
          <el-col :span="9" class="form-block__label">Стоимость / Скидка</el-col>
          <el-col :span="2">
            <form-field :fields="form.fields" :data="form.data" @changeData="changeData" field_name="discount"/>
          </el-col>
          <el-col :span="5">
            <form-field :fields="form.fields" :data="form.data" @changeData="changeData" field_name="cost"
                        :disabled="!form.data.discount"/>
          </el-col>
          <el-col :span="8" class="deal-form__margin_left" title="Промокод">
            <form-field :fields="form.fields" :data="form.data" @changeData="changeData" field_name="mlm_agent"/>
          </el-col>
          <div v-if="field_name in form.errors" class="form-block__errors">
            <div v-for="error in form.errors[field_name]" class="form-block__errors__item">{{ error }}</div>
          </div>
        </el-row>

        <el-row v-else-if="field_name === 'paid'">
          <el-col :span="9" class="form-block__label">Оплачено</el-col>
          <el-col :span="7" title="Нал">
            <form-field :fields="form.fields" :data="form.data" @changeData="changeData" field_name="paid"/>
          </el-col>
          <el-col :span="8" class="deal-form__margin_left" title="Безнал">
            <form-field :fields="form.fields" :data="form.data" @changeData="changeData" field_name="paid_non_cash"/>
          </el-col>
          <div v-if="field_name in form.errors" class="form-block__errors">
            <div v-for="error in form.errors[field_name]" class="form-block__errors__item">{{ error }}</div>
          </div>
        </el-row>

        <el-row v-else>
          <el-col :span="9"
                  class="form-block__label" :class="{'required_field': form.fields[field_name]['required']}">
            {{ form.fields[field_name].label }}
          </el-col>
          <el-col :span="15">
            <form-field :field_name="field_name"
                        :fields="form.fields"
                        :data="form.data"
                        @changeData="changeData"/>
          </el-col>
          <div v-if="field_name in form.errors" class="form-block__errors">
            <div v-for="error in form.errors[field_name]" class="form-block__errors__item">{{ error }}</div>
          </div>
        </el-row>
      </div>

      <div v-if="form.errors.mlm_agent" class="form-group form-block__errors">
        <div v-for="error in form.errors.mlm_agent" class="form-block__errors__item">{{ error }}</div>
      </div>

      <div class="form-group" :class="{'has-errors': 'start_datetime' in form.errors}">
        <el-row>
          <el-col :span="9" class="form-block__label">{{ form.fields['start_datetime'].label }}</el-col>
          <el-col :span="9">
            <form-field field_name="start_datetime"
                        :fields="form.fields"
                        :data="form.data"
                        @changeData="changeData"/>
          </el-col>
          <el-col :span="4">
            <form-field field_name="interval"
                        :fields="form.fields"
                        :data="form.data"
                        the_class="interval"
                        @changeData="changeData"/>
          </el-col>
          <el-col :span="2">
            <el-button class="deal-dnd__form-btn" icon="el-icon-magic-stick" title="Сменить время" @click="dndBegin"/>
          </el-col>

          <div v-if="'start_datetime' in form.errors" class="form-block__errors">
            <div v-for="error in form.errors['start_datetime']" class="form-block__errors__item">{{ error }}</div>
          </div>
        </el-row>
      </div>

      <!-- Persons -->
      <div v-if="person_set" class="formset deal-form__persons">
        <el-row class="deal-form__persons__title">
          <el-col :span="9" class="deal-form__persons__title__txt">{{ person_set.title }}</el-col>
          <el-col :span="15">
            <el-button class="deal-form__persons__btn deal-form__persons__title__btn"
                       icon="el-icon-document-add" @click="personAdd()"/>
          </el-col>
        </el-row>

        <el-row v-for="(formset_item, formset_index) in person_set.data"
                :key="formset_index"
                class="formset__item__row"
                :class="{'has-errors': person_set.formset_errors[formset_index] &&
                                       Object.keys(person_set.formset_errors[formset_index]).length > 0 }">
          <div class="row form-group">
            <el-col class="form-control formset__item" :span="13">
              <el-button-group class="deal-form__persons__btn_group">
                <button type="button"
                        class="el-button deal-form__persons__btn"
                        :class="{'deal-form__persons__btn_act': person_set.data[formset_index].primary}"
                        title="Основной"
                        @click="personChangePrimary(formset_index)">
                  <i :class="{'el-icon-star-on': person_set.data[formset_index].primary,
                              'el-icon-star-off': !person_set.data[formset_index].primary}"></i>
                </button>
                <button type="button"
                        class="el-button deal-form__persons__btn"
                        :class="{'deal-form__persons__btn_act': person_set.data[formset_index].control}"
                        title="Контроль"
                        @click="personChangeControl(formset_index)">
                  <i :class="{'el-icon-success': person_set.data[formset_index].control,
                              'el-icon-circle-check': !person_set.data[formset_index].control}"></i>
                </button>
              </el-button-group>
              <form-field field_name="full_name"
                          class="deal-form__persons__full_name"
                          :fields="person_set.form.fields"
                          :data="person_set.data[formset_index]"
                          :formset_index="formset_index"
                          formset_name="person_set"
                          @changeData="personChangeData"/>
            </el-col>
            <el-col class="form-control formset__item" :span="4">
              <form-field field_name="birthday"
                          :fields="person_set.form.fields"
                          :data="person_set.data[formset_index]"
                          :formset_index="formset_index"
                          formset_name="person_set"
                          @changeData="personChangeData"/>
            </el-col>
            <el-col class="form-control formset__item" :span="7">
              <sip-call label="phone"
                        field_name="phone"
                        :fields="person_set.form.fields"
                        :data="person_set.data[formset_index]"
                        :formset_index="formset_index"
                        formset_name="person_set"
                        @changeData="personChangeData"/>
            </el-col>

            <div v-if="person_set.formset_errors[formset_index] &&
                       Object.keys(person_set.formset_errors[formset_index]).length > 0"
                 class="form-errors">
              <div v-for="(errors, key) in person_set.formset_errors[formset_index]" class="form-errors__item">
                <template v-if="person_set.form.fields[key]">{{ person_set.form.fields[key].label }}:</template>
                <span v-for="error in errors">{{ error }}</span>
              </div>
            </div>

            <div v-for="(_person, _person_index) in person_set.search[formset_index]"
                 :key="_person_index"
                 @click="personSearchPick(formset_index, _person)">
              <el-row class="deal-form__persons__search__row">
                <el-col class="deal-form__persons__search__full_name" :span="13">
                  {{ _person['caсhe']['full_name'] }}
                </el-col>
                <el-col class="deal-form__persons__search__col" :span="4">
                  {{ _person['birthday'] }}
                </el-col>
                <el-col class="deal-form__persons__search__col" :span="7">
                  {{ _person['caсhe']['phone'] }}
                </el-col>
              </el-row>
            </div>

          </div>
          <el-button class="formset__item__delete" icon="el-icon-delete" @click="personDelete(formset_index)"/>
        </el-row>

        <div v-if="Object.keys(person_set.errors).length > 0" class="errors-all has-errors form-errors">
          <div v-for="(error, error_key) in person_set.errors" class="form-errors__item">{{ error }}</div>
        </div>

      </div>
      <!-- End persons -->

      <div class="form-block__footer">
        <template v-if="deal.id && deal.id !== 'add'">
          <el-button v-if="permissions.indexOf('delete') > -1" type="primary" @click="dealSave('delete')">
            <div class="el-button__text">Удалить</div>
          </el-button>
        </template>

        <div class="float-right">
          <el-button-group>
            <el-button type="primary" title="Сохранить" @click="dealSave('save', true)">
              <div class="el-button__text">Сохранить</div>
            </el-button>
            <el-button type="primary" title="Сохранить и закрыть" @click="dealSave('save', false)"
                       icon="el-icon-check"/>
          </el-button-group>
        </div>
        <div class="clearfix"></div>
      </div>

      <el-dialog :visible.sync="closeDealVisible"
                 class="form-block deal-form deal-form-inner"
                 title="Закрытие сделки"
                 width="30%"
                 append-to-body>
        <div class="form-block__footer">
          <el-button type="primary" @click="dealSave('save')">
            <div class="el-button__text">Закрыть с провалом</div>
          </el-button>
          <el-button type="primary" @click="dealSave('save')">
            <div class="el-button__text">Успешное закрытие</div>
          </el-button>
        </div>

        <div v-if="form && form.errors && form.errors.paid" class="form-block__errors">
          <div v-for="error in form.errors.paid" class="form-block__errors__item">{{ error }}</div>
        </div>

      </el-dialog>

    </div>
  </div>
</template>


<script>
  import Vue from 'vue'
  import axios from 'axios'
  import VueAxios from 'vue-axios'
  import DealFormStage from "./DealFormStage";

  Vue.use(VueAxios, axios);

  export default {
    components: {DealFormStage},
    props: ['deal', 'client', 'hide_title'],

    data() {
      return {
        loading: false,
        id: null,
        closeDealVisible: false,
        title: '',
        form: null,
        form_fields_exclude: ['discount', 'mlm_agent', 'paid_non_cash'],
        form_person_exclude: ['birthday', 'email', 'contact_type', 'contact'],
        person_set: null,
        stages: [],
        service_types: [],
        service_set: {},
        permissions: [],
      }
    },

    computed: {
      form_exclude() {
        return ['stage', 'start_datetime', 'finish_datetime', 'interval']
      },
      ordered_fields_filtered() {
        let answer = [];
        for (let key in this.form.ordered_fields) {
          if (this.form_exclude.indexOf(this.form.ordered_fields[key]) === -1 &&
            !this.form_fields_exclude.includes(this.form.ordered_fields[key])
          ) {
            answer.push(this.form.ordered_fields[key]);
          }
        }
        return answer
      }
    },

    watch: {
      deal: function (value, fromValue) {
        if (value && value.id) {
          this.dealLoad();
        }
      },
      title: function (value, fromValue) {
        this.$emit('setTitle', value);
      },
      'form.data.service_type': function (value, fromValue) {
      },
    },

    mounted() {
      if (this.deal.id) {
        this.dealLoad();
      }
    },

    methods: {
      dealLoad() {
        this.loading = true;
        let url = this.$store.getters.root_url + 'deal/';
        if (this.deal.id === 'add') {
          url += 'create/add/';
        } else {
          url += 'edit/' + this.deal.id + '/';
        }
        let params = {
          'get_deal': true,
          'branch': this.$store.state.deal.branch.id ? this.$store.state.deal.branch.id : null,
          'client': this.client ? this.client.id : null,
          'stage': this.deal.stage ? this.deal.stage.id : null,
          'start_iso': this.deal.start_iso ? this.deal.start_iso : null,
          'end_iso': this.deal.end_iso ? this.deal.end_iso : null,
          'master': this.deal.master ? this.deal.master : null,
        };
        if (this.$store.state.deal.drag_drop.drop) {
          params['dnd'] = this.$store.state.deal.drag_drop.id;
          params['start_iso'] = this.$store.state.deal.drag_drop.start_iso;
          params['interval'] = this.$store.state.deal.drag_drop.minutes;
          params['master'] = this.$store.state.deal.drag_drop.master;
        }
        if (this.deal.phone) {
          params.phone = this.deal.phone;
        }
        Vue.axios
          .get(url, {params: params})
          .then(response => {
            this.permissions = response.data.permissions;
            this.id = response.data.id;
            this.title = response.data.title;
            this.stages = response.data.stages;
            this.service_types = response.data.service_types;
            this.person_set = response.data.person_set;
            this.task_form = response.data.task_form;
            this.$emit('tabsSet', response.data.tabs);
            this.form = response.data.form;
            if (this.$store.state.deal.drag_drop.start_iso && this.$store.state.deal.drag_drop.interval) {
              this.form.data.start_datetime =
                this.$moment(this.$store.state.deal.drag_drop.start_iso).format('DD.MM.YYYY HH:mm');
              this.form.data.interval = this.$store.state.deal.drag_drop.interval;
            }
          })
          .catch(error => {
            alert(error);
          })
          .finally(() => {
            this.loading = false;
            if (this.$store.state.deal.drag_drop.drop) {
              this.dealGetCost();
            }
            this.$store.commit('update_drag_drop', {drop: false});
            this.$store.commit('set_drag_drop', {});
            if (!this.form.data['cost']) {
              this.dealGetCost();
            }
          });
      },

      dealSave(action, keep) {
        let url = this.$store.getters.root_url + 'deal/' + action + '/';
        if (action === 'delete' && !confirm('Удалить?')) {
          return
        }
        url += this.deal.id && this.deal.id !== 'add' ? this.deal.id + '/' : '';
        this.loading = true;
        Vue.axios
          .post(url, this.getFormData(this.form.data))
          .then(response => {
            if (response.data.message) {
              this.$message({
                message: response.data.message.text,
                type: response.data.message.type,
                showClose: true
              });
            }
            if (response.data.form && response.data.form.errors
              && response.data.person_set
              && response.data.person_set.errors
              && response.data.person_set.formset_errors) {
              this.form.errors = response.data.form.errors;
              this.person_set.errors = response.data.person_set.errors;
              this.person_set.formset_errors = response.data.person_set.formset_errors;
            } else {
              this.title = response.data.title;
              this.form.data['stage'] = response.data.stage;
              this.centerDialogVisible = false;
              this.form.errors = {};
              this.person_set.errors = {};
              this.person_set.formset_errors = {};
              if (keep) {
                this.$store.commit('set_deal', {'id': response.data.id});
              } else {
                this.$store.commit('set_deal', {'id': null});
              }
              this.$store.commit('set_drag_drop', {});
              this.closeDealVisible = false;
            }
            if (response.data.tabs) {
              this.$emit('tabsSet', response.data.tabs);
            }
          })
          .catch(error => {
            alert(error);
          })
          .finally(() => {
            this.$store.commit('set_refresh_deals', true);
            this.loading = false;
          });
      },

      dealGetCost() {
        let url = this.$store.getters.root_url + 'deal/cost/';
        if (this.form.data.discount) {
          return
        }
        setTimeout(function () {
          Vue.axios
            .post(url, this.getFormData(this.form.data))
            .then(response => {
              this.form.data['cost'] = response.data.cost;
            })
            .catch(error => {
              alert(error);
            })
            .finally(() => {
              // this.loading = false;
            });
        }.bind(this), 10);
      },

      changeData(key, value) {
        this.form.data[key] = value;
        if (['services', 'master', 'discount', 'mlm_agent'].includes(key)) {
          this.dealGetCost();
        }
      },

      getFormData(object) {
        let formData = new FormData();
        formData.append('csrfmiddlewaretoken', this.form.csrf_token);
        formData.append('client', this.client ? this.client.id : null);
        formData.append('deal', this.deal ? this.deal.id : null);

        let formset_data = {};
        for (let key in this.formset) {
          formset_data[key] = this.formset[key].data;
        }
        formData.append('formset', JSON.stringify(formset_data));
        for (let key in object) {
          if (key === 'services') {
            formData.append(key, JSON.stringify(object[key]));
          } else {
            formData.append(key, object[key]);
          }
        }
        formData.append('person_set_data', JSON.stringify(this.person_set.data));
        formData.forEach((value, key) => {
          if (['null'].includes(value)) {
            formData.set(key, '');
          }
        });

        return formData;
      },

      dndBegin() {
        let deal = {
          id: this.deal.id,
          title: this.title,
          master: this.deal.master,
          minutes: this.deal.minutes
        };
        this.$store.commit('set_drag_drop', deal);
        this.$router.push({name: 'deal_schedule'});
        this.centerDialogVisible = false;
        this.$store.commit('set_deal', {'id': null});
      },

      formCancel() {
        this.$store.commit('set_deal', {'id': null});
      },

      personAdd() {
        this.person_set.search = {};
        let new_person = this.clone(this.person_set.form.data);
        this.person_set.data.push(new_person);
        this.dealGetCost();
      },
      personDelete(formset_index) {
        this.person_set.search = {};
        this.person_set.data.splice(formset_index, 1);
        let _primary = false;
        for (let _index in this.person_set.data) {
          if (this.person_set.data[_index].primary) _primary = true;
        }
        if (!_primary && this.person_set.data[0]) this.person_set.data[0].primary = true;

        if (this.person_set.formset_errors[formset_index]) {
          this.person_set.formset_errors.splice(formset_index, 1);
        }
        this.dealGetCost();
      },
      personChangeData(field_name, value, formset_name, formset_index) {
        this.person_set.data[formset_index][field_name] = value;
        if (['control', 'birthday'].includes(field_name)) {
          this.dealGetCost();
        }
        if (['full_name', 'phone'].includes(field_name)) {
          this.personSearch(formset_index);
        }
      },
      personSearch(formset_index) {
        this.person_set.search = {};
        let person = this.person_set.data[formset_index];
        if (person['person_id'] || (person['full_name'].length < 3 && person['phone'].length < 3)) {
          return
        }
        let url = this.$store.getters.root_url + 'identity/person/search/';
        let params = {
          'full_name': person['full_name'],
          'phone': person['phone'],
        };
        Vue.axios
          .get(url, {params: params})
          .then(response => {
            this.person_set.search = {};
            this.person_set.search[formset_index] = response.data.items;
          })
          .catch(error => {
            alert(error);
          })
          .finally(() => {
          });
      },
      personSearchPick(formset_index, _person) {
        this.person_set.data[formset_index].person_id = _person['id'];
        this.person_set.data[formset_index].full_name = _person['caсhe']['full_name'];
        this.person_set.data[formset_index].birthday = _person['birthday'];
        this.person_set.data[formset_index].phone = _person['caсhe']['phone'];
      },

      personChangePrimary(index) {
        if (!this.person_set.data[index].primary) {
          for (let _index in this.person_set.data) {
            this.person_set.data[_index].primary = false;
          }
          this.person_set.data[index].primary = true;
        }
      },
      personChangeControl(index) {
        this.person_set.data[index].control = !!!this.person_set.data[index].control;
        this.dealGetCost();
      },

      clone(obj) {
        if (null == obj || "object" != typeof obj) return obj;
        let copy = obj.constructor();
        for (let attr in obj) {
          if (obj.hasOwnProperty(attr)) copy[attr] = obj[attr];
        }
        return copy;
      },

      pickPerson(field_name, value) {
        let url = this.$store.getters.root_url + 'directory/person/edit/' + value + '/';
        Vue.axios
          .get(url)
          .then(response => {
            let person_data = {
              'primary': false,
              'control': false,
              'person_id': value,
              'full_name': response.data.form.data.last_name + ' '
                + response.data.form.data.first_name + ' ' + response.data.form.data.patronymic,
              'birthday': response.data.form.data.birthday
            };
            for (let key in response.data.formset.phones.data) {
              person_data.phone = response.data.formset.phones.data[key].value;
              break;
            }
            if (this.person_set.data.length === 0 ||
              (this.person_set.data.length > 0 &&
                this.person_set.data[0].full_name === '' && this.person_set.data[0].phone === '')) {
              person_data.primary = true;
              this.person_set.data.splice(0, 1);
            }
            this.set_person_data(this.person_set.data, person_data);
            this.person_find_form.data.person = '';
          })
          .catch(error => {
            console.log(error);
          })
          .finally(() => {
          });
      },

      set_person_data(person_set, data) {
        setTimeout(function run() {
          person_set.push(data);
        }, 10);
      },

    },
  }
</script>


<style>

</style>
