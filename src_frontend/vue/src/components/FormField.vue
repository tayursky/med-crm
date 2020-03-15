<template>

  <el-input v-if="field.widget.attrs.hidden" class="hidden"
            v-model="value"
            :name="field.name"
            :type="field.widget.input_type"/>

  <el-color-picker v-else-if="field.widget.attrs.pick_color"
                   v-model="value"
                   :disabled="_disabled"
                   size="medium"/>

  <masked-input v-else-if="field.widget.attrs.mask"
                v-model="value"
                :name="field.name"
                :disabled="_disabled"
                :mask="field.widget.attrs.mask"
                class="el-input__inner"
                :placeholder="placeholder"/>

  <el-input v-else-if="field.widget.name === 'TextInput' || field.widget.name === 'Textarea'"
            v-widget-attrs="field.widget.attrs"
            v-model="value"
            :disabled="_disabled"
            :name="field.name"
            :type="field.widget.input_type"
            :clearable=true
            :placeholder="placeholder"
            :the_class="the_class"
            autocomplete="off"/>

  <el-switch v-else-if="field.widget.name === 'CheckboxInput'"
             v-widget-attrs="field.widget.attrs"
             v-model="value"
             :disabled="_disabled"
             :name="field.name"
             :type="field.widget.input_type"/>

  <el-date-picker v-else-if="field.widget.attrs.input_type === 'daterange' && from === 'filter'"
                  v-model="value"
                  :disabled="_disabled"
                  type="daterange"
                  start-placeholder="Начало"
                  end-placeholder="Конец"
                  format="dd.MM.yyyy"
                  value-format="dd.MM.yyyy"
                  :name="field.name"
                  :picker-options="picker_options"
                  :placeholder="placeholder"/>

  <el-date-picker v-else-if="field.widget.name === 'DateInput'"
                  v-model="value"
                  :disabled="_disabled"
                  :name="field.name"
                  :type="field.widget.input_type"
                  format="dd.MM.yyyy"
                  value-format="dd.MM.yyyy"
                  :picker-options="picker_options"
                  :placeholder="placeholder"/>

  <el-date-picker v-else-if="field.widget.name === 'DateTimeInput'"
                  v-model="value"
                  :disabled="_disabled"
                  :name="field.name"
                  :type="field.widget.input_type"
                  format="dd.MM.yyyy HH:mm"
                  value-format="dd.MM.yyyy HH:mm"
                  :picker-options="picker_options"
                  :placeholder="placeholder"/>

  <el-time-picker v-else-if="field.widget.name === 'TimeInput'"
                  v-model="value"
                  :disabled="_disabled"
                  :name="field.name"
                  :type="field.widget.input_type"
                  format="HH:mm"
                  value-format="HH:mm"
                  :placeholder="placeholder"/>

  <el-select v-else-if="field.widget.name === 'Select'
              || field.widget.name === 'ParentWidget'
              || field.widget.name === 'SelectMultiple'"
             v-widget-attrs="field.widget.attrs"
             v-model="value"
             :disabled="_disabled"
             :remote="remote"
             :remote-method="remoteSearch"
             :multiple="multiple"
             filterable
             :clearable=true
             :placeholder="placeholder">
    <template v-if="'choices_optgroups' in field.widget">
      <el-option-group v-for="group in options" :key="group.label" :label="group.label">
        <el-option v-for="item in group.options"
                   :key="item.value"
                   :label="item.label"
                   :value="item.value"/>
      </el-option-group>
    </template>
    <template v-else>
      <el-option v-for="item in options"
                 :key="item.value"
                 :label="item.label"
                 :value="item.value"/>
    </template>
  </el-select>

</template>


<script>
  import Vue from 'vue'
  import axios from 'axios'
  import VueAxios from 'vue-axios'

  Vue.use(VueAxios, axios);

  export default {
    props: [
      'field_name', 'fields', 'data', 'the_class', 'disabled',
      'formset_name', 'formset_index', 'from', 'errors', 'perms'
    ],

    data() {
      return {
        value: this.data[this.field_name],
        loading_timeout: null,
        picker_options: {firstDayOfWeek: 1},
      }
    },

    computed: {

      field() {
        return this.fields[this.field_name]
      },

      placeholder() {
        if (this.field.widget.attrs.placeholder) {
          return this.field.widget.attrs.placeholder
        }
        return ''
      },

      options() {
        let choices = this.field.widget.choices;
        if (!choices) {
          choices = []
        }
        if (this.field.widget.attrs.relations) {
          choices = [];
          let available_array = [];
          for (let rel_key in this.field.widget.attrs.relations) {

            // console.log('type', typeof (this.data[rel_key]));
            if (typeof (this.data[rel_key]) === 'object') {
              // Для родительского мультиселекта
              for (let _key in this.data[rel_key]) {
                available_array = available_array.concat(
                  this.field.widget.attrs.relations[rel_key][this.data[rel_key][_key]]
                );
              }
            } else if (this.data[rel_key]) {
              // Для простого родительского селекта
              available_array = this.field.widget.attrs.relations[rel_key][this.data[rel_key]];
            }
            console.log(rel_key, this.data[rel_key]);
          }
          console.log('available_array', available_array);
          choices = this.field.widget.choices.filter(function (item) {
            return available_array.indexOf(item.value) != -1;
          });
          if (available_array.indexOf(this.value) === -1) {
            this.value = null;
          }
        }
        return choices
        // return this.field.widget.choices
      },

      _disabled() {
        if (this.disabled) {
          return 'disabled'
        }
        if (this.from === 'filter') {
          return false
        }
        return !!(this.perms && !this.perms.change) || this.field.widget.attrs.disabled
      },

      remote() {
        return this.field.widget.attrs.remote_search !== undefined
      },

      multiple() {
        return this.field.widget.name === 'SelectMultiple';
      },
    },

    directives: {
      widgetAttrs: {
        inserted: function (el, binding) {
          for (let key in binding.value) {
            el.setAttribute(key, binding.value[key])
          }
        }
      }
    },

    watch: {
      'data': {
        handler: function (value, fromValue) {
          this.value = value[this.field_name];
        },
        deep: true
      },

      value: function (value, fromValue) {
        this.$emit('changeData', this.field_name, value, this.formset_name, this.formset_index);
      },
    },

    mounted() {
      // if (this.field.widget.choices) {
      //   this.options = this.field.widget.choices;
      // }
    },

    methods: {

      test() {
        console.log('test');
      },

      remoteSearch(query) {
        if (this.loading_timeout) clearTimeout(this.loading_timeout);
        this.loading_timeout = setTimeout(function () {
          if (query !== '') {
            this.loading = true;
            let params = {'query': query};
            axios
              .get(this.$store.getters.root_url + this.field.widget.attrs.remote_search, {params})
              .then(response => {
                this.field.widget.choices = response.data.items;
              })
              .catch(error => {
                alert(error);
              })
              .finally(() => {
                this.loading = false;
              });
          } else {
            this.field.widget.choices = [];
          }
        }.bind(this), 500);
      }

    }

  }
</script>


<style>
</style>
