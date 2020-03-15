<template>

  <div>

    <form class="login" @submit.prevent="login">
      <h1>Авторизация</h1>

      <label>Логин</label>
      <input required v-model="username" type="text"/>

      <label>Пароль</label>
      <input required v-model="password" type="password"/>

      <hr/>
      <button type="submit">Login</button>
    </form>

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
        searching: false,
        form: {'fields': {}},
        data: {},
        username: null,
        password: null,
      }
    },
    computed: {
    },
    created() {
    },
    mounted() {
      console.log('Login');
    },
    methods: {

      clientSearch() {
        // this.show = false;
        this.searching = true;
        let params = {};
        Vue.axios.get(this.$store.getters.root_url + 'client/', {params: params})
          .then(response => {
            this.counts = response.data.counts;
            this.result = response.data.result;
            this.show = true;
            this.searching = false;
          })
          .catch(error => {
            console.log(error);
            this.searching = false;
          })
      },

      changeData(key, value) {
        this.data[key] = value;
      },

    }
  }
</script>


<style></style>
