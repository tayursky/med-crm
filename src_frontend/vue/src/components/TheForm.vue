<template>
  <div>
    <div v-if="loading" class="modal-loading"></div>
    <template v-else v-for="field_name in ordered_fields">
      <div v-if="!fields[field_name].widget.attrs.hidden"
           class="form-group" :class="{'has-errors': field_name in errors}">

        <el-row>
          <el-col :span="10"
                  class="form-block__label"
                  :class="{'required_field': fields[field_name]['required']}">
            {{ fields[field_name].label }}
          </el-col>

          <el-col :span="14">
            <form-field :field_name="field_name"
                        :fields="fields"
                        :data="data"
                        :perms="perms"
                        @changeData="changeData"/>
          </el-col>

          <div v-if="field_name in errors" class="form-block__errors">
            <div v-for="error in errors[field_name]" class="form-block__errors__item">{{ error }}</div>
          </div>
        </el-row>

        <div v-show="errors" class="form-block__errors">
          <div v-for="error in errors.__all__" class="form-block__errors__item">{{ error }}</div>
        </div>

      </div>
    </template>

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
        <el-button v-if="perms.change"
                   class="formset__item__add"
                   icon="el-icon-document-add"
                   @click="formsetAdd(formset_name)">
        </el-button>
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

            <sip-call v-if="$store.state.deal.settings.sip_id && formset_name === 'phones' && field_name === 'value'"
                      label="value"
                      :field_name="field_name"
                      :fields="formset[formset_name].form.fields"
                      :data="formset[formset_name].data[formset_index]"
                      :formset_name="formset_name"
                      :formset_index="formset_index"
                      :perms="perms"
                      @changeData="formsetChangeData"/>

            <form-field v-else
                        :field_name="field_name"
                        :fields="formset[formset_name].form.fields"
                        :data="formset[formset_name].data[formset_index]"
                        :formset_name="formset_name"
                        :formset_index="formset_index"
                        :perms="perms"
                        @changeData="formsetChangeData"/>
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
        <el-button v-if="perms.change"
                   class="formset__item__delete"
                   icon="el-icon-delete"
                   @click="formsetDelete(formset_name, formset_index)">
        </el-button>
      </el-row>
    </div>
    <!-- End formset -->

    <div slot="footer" class="form-block__footer">
      <el-button v-if="item.id && perms.delete" type="primary" @click="formSave('delete')">
        <div class="el-button__text">Удалить</div>
      </el-button>
      <div class="float-right">
        <el-button v-if="perms.change" type="primary" @click="formSave('save')">
          <div class="el-button__text">Сохранить</div>
        </el-button>
      </div>
      <div class="clearfix clear clea"></div>
    </div>

  </div>
</template>


<script>
  import Vue from 'vue'
  import axios from 'axios'
  import VueAxios from 'vue-axios'

  Vue.use(VueAxios, axios);

  export default {
    props: ['app_label', 'model_name', 'item',],
    data() {
      return {
        loading: false,
        url: '',
        data: {},
        csrf_token: '',
        parents: [],
        fields: {},
        fieldsets: [],
        ordered_fields: [],
        errors: {},
        formset: {},
        formset_list: [],
        formset_errors: {},
        permissions: []
      }
    },

    computed: {
      perms() {
        let _perms = {
          'view': !!(this.permissions && this.permissions.indexOf('view') > -1),
          'change': !!(this.permissions && this.permissions.indexOf('change') > -1),
          'delete': !!(this.permissions && this.permissions.indexOf('delete') > -1),
        };
        return _perms
      },
    },

    watch: {
      item: function (toVal, fromVal) {
        if (toVal.id && !this.loading) {
          this.formLoad();
        }
      }
    },

    mounted() {
      this.formLoad();
    },

    methods: {
      formLoad() {
        this.loading = true;
        this.fields = {};
        this.fieldsets = [];
        this.ordered_fields = [];
        this.errors = {};
        this.formset = {};
        this.formset_list = [];
        this.formset_errors = {};
        let params = {
          'model_name': this.model_name,
          'initial': this.item.initial ? this.item.initial : null
        };
        let url = this.$store.getters.root_url + this.app_label + '/' + this.model_name;
        if (this.item.id === 'add') {
          url += '/create/';
        } else {
          url += '/edit/' + this.item.id + '/';
        }
        if (this.item.phone) {
          params.phone = this.item.phone;
        }
        // for (let key in this.item) {
        //   if (key !== 'id') {
        //     params[key] = this.item[key];
        //   }
        // }
        Vue.axios
          .get(url, {params: params})
          .then(response => {
            this.$emit('setVerboseName', response.data.form.verbose_name);
            this.csrf_token = response.data.form.csrf_token;
            this.parents = response.data.parents;
            this.data = response.data.form.data;
            this.ordered_fields = response.data.form.ordered_fields;
            this.fields = response.data.form.fields;
            this.errors = response.data.form.errors;
            this.formset = response.data.formset;
            this.formset_list = response.data.formset_list;
            this.formset_errors = response.data.formset_errors;
            this.permissions = response.data.permissions;
            if (response.data.title) {
              this.$emit('setTitle', response.data.title);
            }
            if (this.item.id === 'add' && this.item.filters) {
              for (let key in this.item.filters.data) {
                let value = this.item.filters.data[key];
                if (value && typeof value === 'object') {
                  value = value[0];
                }
                this.data[key] = value;
              }
            }
            if (response.data.tabs) {
              this.$emit('tabsSet', response.data.tabs);
            }
          })
          .catch(error => {
            console.log(error);
          })
          .finally(() => {
            this.loading = false;
          });
      },

      formSave(action) {
        let url = this.$store.getters.root_url + this.app_label + '/' + this.model_name + '/' + action + '/';
        if (action === 'delete' && !confirm('Удалить?')) {
          return
        }
        url += this.item.id && this.item.id !== 'add' ? this.item.id + '/' : '';
        Vue.axios
          .post(url, this.getFormData(this.data))
          .then(response => {
            if (response.data.message) {
              this.$message({
                message: response.data.message.text, type: response.data.message.type, showClose: true
              });
            }
            if (response.data.form && (response.data.form.errors || response.data.formset_errors)) {
              this.errors = response.data.form.errors;
              this.formset_errors = response.data.formset_errors;
            } else {
              this.errors = {};
              this.formset_errors = {};
              this.$emit('itemClose');
              if (response.data.id) {
                this.$emit('itemRefresh', response.data.id);
              }
            }
          })
          .catch(error => {
            console.log(error);
          })
          .finally(() => {
            this.loading = false;
          });
        // console.log(this.formset);
      },

      changeData(key, value) {
        this.data[key] = value;
      },

      getFormData(object) {
        let formData = new FormData();
        formData.append('csrfmiddlewaretoken', this.csrf_token);
        let formset_data = {};
        for (let key in this.parents) {
          if (this.item[this.parents[key]]) {
            formData.append(this.parents[key], this.item[this.parents[key]])
          }
        }
        for (let key in this.formset) {
          formset_data[key] = this.formset[key].data;
        }
        formData.append('formset', JSON.stringify(formset_data));

        for (let key in object) {
          if (object[key]) {
            formData.append(key, object[key]);
          }
        }
        return formData;
      },

      formsetAdd(formset_name) {
        let new_data = this.clone(this.formset[formset_name].form.data);
        this.formset[formset_name].data.push(new_data);
      },
      formsetDelete(formset_name, index) {
        this.formset[formset_name].data.splice(index, 1);
        if (this.formset_errors[formset_name] && this.formset_errors[formset_name][index]) {
          this.formset_errors[formset_name].splice(index, 1);
        }
      },
      formsetChangeData(field_name, value, formset_name, formset_index) {
        // console.log('formsetChangeData', field_name, value, formset_name, formset_index);
        this.formset[formset_name].data[formset_index][field_name] = value;
      },

      clone(obj) {
        if (null == obj || 'object' != typeof obj) return obj;
        let copy = obj.constructor();
        for (let attr in obj) {
          if (obj.hasOwnProperty(attr)) copy[attr] = obj[attr];
        }
        return copy;
      }

    }
  }
</script>


<style>

</style>
