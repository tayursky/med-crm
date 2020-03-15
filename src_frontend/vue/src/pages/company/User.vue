<template>
  <div>
    <div class="loading" v-if="loading"></div>

    <div v-else class="form-block">

      <div style="padding: 0 0 5px; display: inline-block; width: 100%;">
        <div class="float-right">
          <el-button icon="el-icon-refresh" @click="userLoad"></el-button>
        </div>
      </div>

      <el-row v-if="permissions.includes('add')" class="deal-form__person_title">
        <el-col :span=10 class="deal-form__person_title__txt">Найти и создать сотрудника</el-col>
        <el-col :span=14 class="deal-form__person_search">
          <form-field field_name="person"
                      :fields="person_find_form.fields"
                      :data="person_find_form.data"
                      placeholder="При выборе создается новый пользователь"
                      @changeData="pickPerson"/>
        </el-col>
      </el-row>

      <div v-for="field_name in ordered_fields" class="form-group" :class="{'has-errors': field_name in errors}">
        <el-row>
          <el-col :span="10" class="form-block__label" :class="{'required_field': fields[field_name]['required']}">
            {{ fields[field_name].label }}
          </el-col>
          <el-col :span="14">
            <form-field :field_name="field_name" :fields="fields" :data="data" @changeData="changeData"/>
          </el-col>
          <div v-if="field_name in errors" class="form-block__errors">
            <div v-for="error in errors[field_name]" class="form-block__errors__item">{{ error }}</div>
          </div>
        </el-row>
        <div v-if="errors" class="form-block__errors">
          <div v-for="error in errors.__all__" class="form-block__errors__item">{{ error }}</div>
        </div>
      </div>

      <!-- Formset -->
      <div v-for="(formset_name, index) in formset_list" class="formset">

        <div class="formset__title">{{ formset[formset_name].label }}</div>
        <div class="formset__item__row">
          <el-row class="formset__head">
            <template v-for="(field_name, index) in formset[formset_name].form.ordered_fields">
              <el-col v-if="!formset[formset_name].form.fields[field_name].widget.attrs.hidden"
                      :span="formset[formset_name].form.fields[field_name].widget.attrs.el_col"
                      class="formset__head__item">
                {{ formset[formset_name].form.fields[field_name].label }}
              </el-col>
            </template>
          </el-row>
          <el-button class="formset__item__add" icon="el-icon-document-add" @click="formsetAdd(formset_name)"/>
        </div>

        <el-row v-for="(formset_item, formset_index) in formset[formset_name].data"
                :key="formset_index"
                class="formset__item__row"
                :class="{'has-errors': formset_errors[formset_name] && formset_errors[formset_name][formset_index] &&
                        Object.keys(formset_errors[formset_name][formset_index]).length > 0}">
          <div class="row form-group">
            <el-col v-for="(field_name, index) in formset[formset_name].form.ordered_fields"
                    :key="field_name"
                    :span="formset[formset_name].form.fields[field_name].widget.attrs.el_col"
                    class="form-control formset__item">
              <form-field :field_name="field_name"
                          :fields="formset[formset_name].form.fields"
                          :data="formset[formset_name].data[formset_index]"
                          :formset_name="formset_name"
                          :formset_index="formset_index"
                          @changeData="changeFormsetData"/>
            </el-col>

            <div v-if="formset_errors[formset_name] && formset_errors[formset_name][formset_index] &&
               Object.keys(formset_errors[formset_name][formset_index]).length > 0"
                 class="form-errors">
              <div v-for="(errors, key) in formset_errors[formset_name][formset_index]" class="form-errors__item">
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

      <!-- Groups -->
      <div v-if="groups_select" class="form-block__groups formset">
        <div class="formset__title">Группы доступа</div>
        <div class="form-block__groups__select">
          <el-select v-model="groups.selected" placeholder="Выберите группу">
            <el-option v-for="item in groups_select"
                       :key="item.id"
                       :label="item.name"
                       :value="item.id"/>
          </el-select>
        </div>
        <div class="form-block__groups__user_groups">
          <div v-for="group in groups.user_groups"
               :key="group"
               class="form-block__groups__user_groups__item"
               @click="groupRemove(group)">
            {{ groups.all[group] }}<i class="el-dialog__close el-icon el-icon-close"></i>
          </div>
        </div>
      </div>
      <!-- End groups -->

      <div slot="footer" class="form-block__footer">
        <el-button v-if="user_id" type="primary" @click="formSave('delete')">
          <div class="el-button__text">Удалить</div>
        </el-button>
        <div class="float-right">
          <el-button type="primary" @click="formSave('save')">
            <div class="el-button__text">Сохранить</div>
          </el-button>
        </div>
      </div>
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
        centerDialogVisible: false,
        loading: false,
        verbose_name: '',
        url: '',
        data: {},
        csrf_token: '',
        fields: {},
        fieldsets: [],
        ordered_fields: [],
        errors: {},
        person_find_form: null,
        formset: {},
        formset_list: [],
        formset_errors: {},
        groups: [],
        user_id: null,
        permissions: []
      }
    },

    computed: {
      groups_select() {
        let list = [];
        for (let id in this.groups.all) {
          let group = this.groups.all[id];
          // console.log(id, this.groups.user_groups.indexOf(parseInt(id)) === -1);
          if (this.groups.user_groups.indexOf(parseInt(id)) === -1) {
            list.push({'id': id, 'name': group})
          }
        }
        return list
      },
    },

    watch: {
      centerDialogVisible(toVal, fromVal) {
        if (toVal === false) {
          this.formCancel();
        }
      },
      'groups.selected'(val, fromVal) {
        // console.log('groups.selected', val);
        if (this.groups.user_groups.indexOf(parseInt(val)) === -1) {
          this.groups.user_groups.push(parseInt(val));
        }
      },
    },

    mounted() {
      this.user_id = this.$route.params.user_id;
      this.userLoad();
    },

    methods: {

      userLoad() {
        this.centerDialogVisible = true;
        this.loading = true;
        let params = {'get': true};
        let url = this.$store.getters.root_url + 'company/user/' + this.user_id + '/';
        Vue.axios.get(url, {params: params})
          .then(response => {
            this.csrf_token = response.data.form.csrf_token;
            this.verbose_name = response.data.form.verbose_name;
            this.data = response.data.form.data;
            this.ordered_fields = response.data.form.ordered_fields;
            this.fields = response.data.form.fields;
            this.errors = response.data.form.errors;
            this.person_find_form = response.data.person_find_form;
            this.formset = response.data.formset;
            this.formset_list = response.data.formset_list;
            this.formset_errors = response.data.formset_errors;
            this.groups = response.data.groups;
            this.permissions = response.data.permissions;
          })
          .catch(error => {
            alert(error);
          })
          .finally(() => {
            this.loading = false;
          });
        // console.log('this.fields', this.fields);
      },

      pickPerson(field_name, value) {
        let url = this.$store.getters.root_url + 'company/user/' + value + '/create/';
        Vue.axios
          .get(url, {params: {'create_from_person': true}})
          .then(response => {
            this.$router.push({name: 'company_user', params: {'user_id': response.data.user}});
            this.user_id = response.data.user;
            this.userLoad();
          })
          .catch(error => {
            console.log(error);
          })
          .finally(() => {
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
        formData.append('groups', JSON.stringify(this.groups.user_groups));
        Object.keys(object).forEach(
          key => formData.append(key, object[key])
        );
        return formData;
      },

      formSave(action) {
        let url = this.$store.getters.root_url + 'company/user/' + this.user_id + '/' + action + '/';
        if (action === 'delete' && !confirm('Удалить?')) {
          return
        }
        Vue.axios
          .post(url, this.getFormData(this.data))
          .then(response => {
            if (response.data.errors && response.data.formset_errors) {
              this.errors = response.data.errors;
              this.formset_errors = response.data.formset_errors;
            } else {
              this.errors = {};
              this.formset_errors = {};
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
            console.log(error);
          });
        console.log(this.formset);
      },

      formCancel() {
        this.loading = false;
        this.$emit('itemClose');
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

      groupRemove(group) {
        let index = this.groups.user_groups.indexOf(group);
        this.groups.user_groups.splice(index, 1);
      },

    }
  }
</script>


<style>

</style>
