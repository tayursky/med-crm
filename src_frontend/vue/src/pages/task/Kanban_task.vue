<template>
  <el-dialog
      class="form-block"
      :visible.sync="centerDialogVisible"
      :title="this.verbose_name"
      @keyup.enter="save"
      @keyup.esc="cancel"
  >
    <div class="modal-loading" v-if="loading"></div>

    <div v-else
         class="form-group"
         :class="{'has-errors': field_name in errors}"
         v-for="field_name in ordered_fields">

      <el-row>
        <el-col :span="10"
                class="el-dialog__label"
                :class="{'required_field': fields[field_name]['required']}"
        >
          {{ fields[field_name].label }}
        </el-col>

        <el-col :span="14">
          <form-field :field_name="field_name"
                      :fields="fields"
                      :data="data"
                      @changeData="changeData"/>
        </el-col>

        <div v-if="field_name in errors"
             class="el-dialog__errors"
        >
          <div v-for="error in errors[field_name]"
               class="el-dialog__errors__item"
          >
            {{ error }}
          </div>
        </div>
      </el-row>

      <div v-show="errors"
           class="el-dialog__errors"
      >
        <div v-for="error in errors.__all__"
             class="el-dialog__errors__item"
        >
          {{ error }}
        </div>
      </div>

    </div>

    <!-- Persons -->
    <el-row v-if="person_find_form" class="row form-group">
      <el-col :span="10"
              class="el-dialog__label">
        {{ person_find_form.fields.person.label }} {{ person_find_form.data.person }}
      </el-col>
      <el-col :span="14">
        <form-field field_name="'person'"
                    :fields="person_find_form.fields"
                    :data="person_find_form.data"
                    :root_url="root_url"
                    @changeData="pickPerson"/>
      </el-col>
    </el-row>

    <div v-for="(person, person_index) in person_list">
      <p style="padding: 3px 5px; text-align: right">
        {{ person.first_name }} {{ person.patronymic }} {{ person.last_name }} ({{ person.phone }})
      </p>
    </div>
    <!-- End persons -->

    <!-- Formset -->

    <div v-for="(formset_name, index) in formset_list"
         class="formset">
      <div class="formset__title">{{ formset[formset_name].label }}</div>
      <div class="formset__item__row">
        <el-row class="formset__head">
          <template v-for="(field_name, index) in formset[formset_name].form.ordered_fields">
            <el-col :span="formset[formset_name].form.fields[field_name].widget.attrs.el_col"
                    class="formset__head__item">
              {{ formset[formset_name].form.fields[field_name].label }}
            </el-col>
          </template>
        </el-row>
        <el-button class="formset__item__add"
                   icon="el-icon-document-add"
                   @click="formsetAdd(formset_name)">
        </el-button>
      </div>

      <el-row :key="formset_index"
              class="formset__item__row"
              :class="{'has-errors': formset_errors[formset_name] && formset_errors[formset_name][formset_index] &&
              Object.keys(formset_errors[formset_name][formset_index]).length > 0}"
              v-for="(formset_item, formset_index) in formset[formset_name].data"
      >
        <div class="row form-group">
          <el-col :span="formset[formset_name].form.fields[field_name].widget.attrs.el_col"
                  :key="field_name"
                  class="form-control formset__item"
                  v-for="(field_name, index) in formset[formset_name].form.ordered_fields">
            <form-field :field_name="field_name"
                        :fields="formset[formset_name].form.fields"
                        :data="formset[formset_name].data[formset_index]"
                        :formset_name="formset_name"
                        :formset_index="formset_index"
                        @changeData="changeFormsetData"
            />
          </el-col>

          <div class="form-errors"
               v-if="formset_errors[formset_name] && formset_errors[formset_name][formset_index] &&
               Object.keys(formset_errors[formset_name][formset_index]).length > 0">
            <div class="form-errors__item"
                 v-for="(errors, key) in formset_errors[formset_name][formset_index]">
              {{ formset[formset_name].form.fields[key].label }}:
              <span v-for="error in errors">{{ error }}</span>
            </div>
          </div>

        </div>
        <el-button class="formset__item__delete"
                   icon="el-icon-delete"
                   @click="formsetDelete(formset_name, formset_index)">
        </el-button>

      </el-row>
    </div>

    <!-- End formset -->

    <div slot="footer">
      <div class="left-block">
        <el-button v-if="task.id" type="primary" @click="formSave('delete')">
          <div class="el-button__text">Удалить</div>
        </el-button>
      </div>
      <el-button type="primary" @click="formSave('save')">
        <div class="el-button__text">Сохранить</div>
      </el-button>
    </div>

  </el-dialog>
</template>


<script>
  import Vue from 'vue'
  import axios from 'axios'
  import VueAxios from 'vue-axios'

  Vue.use(VueAxios, axios);

  export default {
    props: ['root_url', 'task'],
    data() {
      return {
        centerDialogVisible: false,
        verbose_name: '',
        loading: false,
        person_find_form: null,
        person_data: {},
        person_list: [],
        data: {},
        csrf_token: '',
        fields: {},
        fieldsets: [],
        ordered_fields: [],
        errors: {},
        formset: {},
        formset_list: [],
        formset_errors: {}
      }
    },

    computed: {},

    watch: {
      centerDialogVisible: function (toVal, fromVal) {
        if (toVal === false) {
          this.formCancel();
        }
      },
      task: function (toVal, fromVal) {
        console.log('watch task', toVal.id);
        if (toVal.id) {
          this.loadForm();
        }
      },
    },

    mounted() {
    },

    methods: {

      loadForm() {
        this.centerDialogVisible = true;
        this.loading = true;
        let url = this.$store.getters.root_url + 'task/kanban/task/';
        console.log('loadForm', this.task);
        if (this.task.id === 'add') {
          url += 'create/add/';
        } else {
          url += 'edit/' + this.task.id + '/';
        }
        let params = {
          'service': this.task.service_id ? this.task.service_id : null,
          'step': this.task.step ? this.task.step.id : null,
        };
        Vue.axios.get(url, {params: params})
          .then(response => {
            this.csrf_token = response.data.form.csrf_token;
            this.verbose_name = response.data.form.verbose_name;
            this.data = response.data.form.data;
            this.ordered_fields = response.data.form.ordered_fields;
            this.fields = response.data.form.fields;
            this.errors = response.data.form.errors;
            this.formset = response.data.formset;
            this.formset_list = response.data.formset_list;
            this.formset_errors = response.data.formset_errors;
            this.person_find_form = response.data.person_find_form;
            this.person_list = response.data.person_list;
            this.loading = false;
          })
          .catch(error => {
            this.loading = false;
            console.log(error);
          });
      },

      changeData(key, value) {
        this.data[key] = value;
      },

      getFormData(object) {
        let formData = new FormData();
        formData.append('csrfmiddlewaretoken', this.csrf_token);
        let formset_data = {};
        for (let key in this.formset) {
          formset_data[key] = this.formset[key].data;
        }
        formData.append('formset', JSON.stringify(formset_data));
        Object.keys(object).forEach(
          key => formData.append(key, object[key])
        );

        let person_list = [];
        for (let key in this.person_list) {
          person_list.push(this.person_list[key].id);
        }
        formData.append('person_list', JSON.stringify(person_list));

        return formData;
      },

      formSave(action) {
        let url = this.$store.getters.root_url + 'task/kanban/task/' + action + '/';
        if (action === 'delete' && !confirm('Удалить?')) {
          return
        }
        url += this.task.id && this.task.id !== 'add' ? this.task.id + '/' : '';
        Vue.axios.post(url, this.getFormData(this.data))
          .then(response => {
            if (response.data.form && response.data.form.errors && response.data.formset_errors) {
              this.errors = response.data.form.errors;
              this.formset_errors = response.data.formset_errors;
            } else {
              this.errors = {};
              this.formset_errors = {};
              this.centerDialogVisible = false;
            }
          })
          .catch(error => {
            console.log(error);
          });
        console.log(this.formset);
      },

      formCancel() {
        this.loading = false;
        this.$emit('closeTask');
      },

      formsetAdd(formset_name) {
        let new_data = this.clone(this.formset[formset_name].form.data);
        this.formset[formset_name].data.push(new_data);
      },

      formsetDelete(formset_name, index) {
        // console.log('formsetDelete');
        this.formset[formset_name].data.splice(index, 1);
        if (this.formset_errors[formset_name] && this.formset_errors[formset_name][index]) {
          this.formset_errors[formset_name].splice(index, 1);
        }
      },

      changeFormsetData(field_name, value, formset_name, formset_index) {
        console.log('changeFormsetData', field_name, value, formset_name, formset_index);
        this.formset[formset_name].data[formset_index][field_name] = value;
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
        // console.log(field_name, value);
        let url = this.$store.getters.root_url + 'directory/person/edit/' + value + '/';
        Vue.axios.get(url)
          .then(response => {
            // console.log(response.data.form.data);
            let person_data = {};
            person_data.first_name = response.data.form.data.first_name;
            person_data.patronymic = response.data.form.data.patronymic;
            person_data.last_name = response.data.form.data.last_name;
            person_data.id = value;
            for (let key in response.data.formset.phones.data) {
              person_data.phone = response.data.formset.phones.data[key].value;
              break;
            }
            this.person_list.push(person_data);
            this.loading = false;
          })
          .catch(error => {
            this.loading = false;
            console.log(error);
          });

      }

    }
  }
</script>


<style>

</style>
