<template>

  <div class="model_filter" @keyup.enter="upEnter">
    <template v-if="filters">
      <div v-for="field_name in filters.ordered" class="model_filter__item">

        <label class="model_filter__label"><span>{{ filters.fields[field_name].label }}</span></label>
        <div class="model_filter__filter">
          <form-field :field_name="field_name"
                      :fields="filters.fields"
                      :data="filters.data"
                      @changeData="changeData"/>
        </div>

      </div>
    </template>
  </div>

</template>


<script>
  export default {
    props: ['filters'],
    data() {
      return {
        data: {},
      }
    },

    computed: {
    },

    watch: {
      filters: function (value, fromValue) {
        // console.log('watch filters', fromValue, '>', value);
      },
    },

    mounted() {
    },

    methods: {

      changeData(key, value) {
        // console.log('changeData', key, value);
        this.$emit('changeFilters', key, value);
      },

      get_int(key, value) {
        if (!value) {
          return ''
        } else if (this.filters.fields[key].widget.name === 'DateInput' ||
          this.filters.fields[key].widget.name === 'DateTimeInput') {
          return value;
        } else if (/^(\-|\+)?([0-9]+|Infinity)$/.test(value)) {
          return Number(value);
        }
        return value
      },

      upEnter() {
        console.log('upEnter');
        this.$emit('refresh');
      }

    }
  }
</script>


<style>

</style>
