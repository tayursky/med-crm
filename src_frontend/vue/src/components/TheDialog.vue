<template>
  <el-dialog class="form-block"
             :visible.sync="dialog_visible"
             :title="verbose_name"
             :close-on-click-modal="false"
             @keyup.enter="save"
             @keyup.esc="cancel">

    <the-form :app_label="app_label"
              :model_name="model_name"
              :item="item"
              :permissions="permissions"
              @setDialogVisible="setDialogVisible"
              @setVerboseName="setVerboseName"
              @itemClose="itemClose"/>
  </el-dialog>
</template>


<script>
  import Vue from 'vue'
  import axios from 'axios'
  import VueAxios from 'vue-axios'

  Vue.use(VueAxios, axios);

  export default {
    props: ['app_label', 'model_name', 'item', 'permissions'],
    data() {
      return {
        dialog_visible: false,
        verbose_name: '',
      }
    },
    mounted() {
    },

    computed: {},

    watch: {
      dialog_visible: function (toVal, fromVal) {
        if (toVal === false) {
          this.$emit('itemClose');
          // this.$emit('itemClose', false);
        }
      },
      item: function (toVal, fromVal) {
        this.dialog_visible = !!(toVal.id);
      }
    },

    methods: {
      setDialogVisible(value) {
        this.dialog_visible = value;
      },
      setVerboseName(value) {
        console.log('setVerboseName');
        this.verbose_name = value;
      },
      itemClose() {
        this.$emit('itemClose');
      }
    }
  }
</script>


<style>

</style>
