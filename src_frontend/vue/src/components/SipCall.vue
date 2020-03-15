<template>
  <div class="sip-call">

    <form-field :field_name="field_name"
                :fields="fields"
                :data="data"
                :formset_index="formset_index"
                :formset_name="formset_name"
                @changeData="changeData"/>

    <button v-if="$store.state.deal.settings.sip_id"
            type="button"
            class="el-button"
            @click="sipCall">
      <i class="el-icon-phone-outline"></i>
    </button>

  </div>
</template>


<script>
  import Vue from 'vue'
  import axios from 'axios'
  import VueAxios from 'vue-axios'

  Vue.use(VueAxios, axios);

  export default {
    props: ['label', 'field_name', 'fields', 'data', 'formset_index', 'formset_name'],
    data() {
      return {}
    },

    computed: {},

    watch: {},

    mounted() {
    },

    methods: {
      changeData(field_name, value, formset_name, formset_index) {
        this.$emit('changeData', field_name, value, formset_name, formset_index);
      },

      getFormData(object) {
        let formData = new FormData();
        Object.keys(object).forEach(
          key => formData.append(key, object[key])
        );
        return formData;
      },

      sipCall() {
        console.log('sipCall');
        if (!this.data) {
          return false
        }
        this.loading = true;
        let params = {
          'phone': this.data[this.label]
        };
        // .post(this.$store.getters.root_url + 'sip/mightycall/webhook/', this.getFormData(params))
        // .get(this.$store.getters.root_url + 'sip/make_call/', {params: params})
        Vue.axios
          .get(this.$store.getters.root_url + 'sip/make_call/', {params: params})
          .then(response => {
            if (response.data.message) {
              this.$message({
                message: response.data.message.text, type: response.data.message.type, showClose: true
              });
            }
          })
          .catch(error => {
            console.log(error);
          })
          .finally(() => {
            this.loading = false;
          });
      },

    }
  }
</script>


<style>

</style>
