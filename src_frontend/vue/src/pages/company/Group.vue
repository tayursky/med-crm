<template>
  <div class="user-group">
    <div class="loading" v-if="loading"></div>

    <div v-else class="form-block">

      <div style="padding: 0 0 5px; display: inline-block; width: 100%;">
        <div class="float-right">
          <el-button icon="el-icon-refresh" @click="groupLoad"></el-button>
        </div>
      </div>

      <template v-if="form">
        <div class="form-group"
             :class="{'has-errors': field_name in form.errors}"
             v-for="field_name in form.ordered_fields">
          <el-row>
            <el-col :span="10"
                    class="form-block__label"
                    :class="{'required_field': form.fields[field_name]['required']}">
              {{ form.fields[field_name].label }}
            </el-col>

            <el-col :span="14">
              <form-field :field_name="field_name"
                          :fields="form.fields"
                          :data="form.data"
                          @changeData="changeData"/>
            </el-col>

            <div v-if="field_name in form.errors"
                 class="form-block__errors">
              <div v-for="error in form.errors[field_name]" class="form-block__errors__item">
                {{ error }}
              </div>
            </div>
          </el-row>

          <div v-if="form.errors" class="form-block__errors">
            <div v-for="error in form.errors.__all__" class="form-block__errors__item">{{ error }}</div>
          </div>
        </div>

        <!-- Permissions -->
        <div class="permissions">
          <div class="permissions__title">
            <div class="permissions__title__txt">Права доступа</div>
          </div>
          <table class="permissions__table">
            <thead>
            <tr>
              <td>id</td>
              <td>app_label</td>
              <td>content_type</td>
              <td>codename</td>
              <td>name</td>
              <td></td>
            </tr>
            </thead>
            <tbody>
            <tr v-for="perm in perms"
                :key="perm.id" data-perm_id="perm.id"
                class="permissions__table__tr"
                @click="clickPerm(perm)">
              <td class="permissions__table__td">{{ perm.id }}</td>
              <td class="permissions__table__td">{{ perm.app_label }}</td>
              <td class="permissions__table__td">{{ perm.content_type }}</td>
              <td class="permissions__table__td">{{ perm.codename }}</td>
              <td class="permissions__table__td">{{ perm.name }}</td>
              <td class="permissions__table__td">
                <i v-if="group_perms.indexOf(perm.id) !== -1" class="el-icon el-icon-check"></i>
              </td>
            </tr>
            </tbody>
          </table>
        </div>
        <!-- End permissions -->

        <div slot="footer" class="form-block__footer">
          <el-button v-if="group_id" type="primary" @click="formSave('delete')">
            <div class="el-button__text">Удалить</div>
          </el-button>
          <div class="float-right">
            <el-button type="primary" @click="formSave('save')">
              <div class="el-button__text">Сохранить</div>
            </el-button>
          </div>
        </div>

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
        centerDialogVisible: false,
        loading: false,
        url: '',
        group_id: null,
        group_perms: [],
        perms: null,
        form: null,
      }
    },

    computed: {
    },

    watch: {
      centerDialogVisible(toVal, fromVal) {
        if (toVal === false) {
          this.formCancel();
        }
      },
    },

    mounted() {
      this.group_id = this.$route.params.group_id;
      this.groupLoad();
    },

    methods: {

      groupLoad() {
        this.centerDialogVisible = true;
        this.loading = true;
        let params = {'get': true};
        let url = this.$store.getters.root_url + 'company/group/' + this.group_id + '/';
        Vue.axios.get(url, {params: params})
          .then(response => {
            this.form = response.data.form;
            this.group_perms = response.data.group_perms;
            this.perms = response.data.perms;
            this.loading = false;
          })
          .catch(error => {
            this.loading = false;
            console.log(error);
          });
        // console.log('this.fields', this.fields);
      },

      changeData(key, value) {
        this.form.data[key] = value;
      },

      getFormData(object) {
        let formData = new FormData();
        formData.append('csrfmiddlewaretoken', this.form.csrf_token);
        formData.append('group_perms', JSON.stringify(this.group_perms));
        Object.keys(object).forEach(
          key => formData.append(key, object[key])
        );
        return formData;
      },

      formSave(action) {
        let url = this.$store.getters.root_url + 'company/group/' + this.group_id + '/' + action + '/';
        if (action === 'delete' && !confirm('Удалить?')) {
          return
        }
        Vue.axios.post(url, this.getFormData(this.form.data))
          .then(response => {
            if (response.data.errors) {
              this.form.errors = response.data.errors;
            } else {
              this.form.errors = {};
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
      },

      formCancel() {
        this.loading = false;
        this.$emit('itemClose');
      },

      clickPerm(perm) {
        let index = this.group_perms.indexOf(perm.id);
        if (index !== -1) {
          this.group_perms.splice(index, 1);
        } else {
          this.group_perms.push(perm.id);
        }
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


<style>

</style>
