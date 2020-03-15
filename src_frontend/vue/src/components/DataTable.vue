<template>
  <div>

    <table class="data-table">
      <thead>
      <tr>
        <th v-for="head in headers">
          {{ head.text }}
        </th>
      </tr>
      </thead>

      <tbody>
      <tr v-for="item in items" @click="editItem(item)">
        <td v-for="head in headers">
          {{ item[head.value] }}
        </td>
      </tr>
      </tbody>

    </table>

  </div>
</template>


<script>
  export default {
    props: ['headers', 'items'],
    data() {
      return {}
    },

    computed: {},

    watch: {
      items: function (value, fromValue) {
        // console.log('watch items', value);
      }
    },

    mounted() {
    },

    methods: {

      editItem(item) {
        this.$emit('editItem', item);
      },

    }
  }
</script>


<style>

</style>
