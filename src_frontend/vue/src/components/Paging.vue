<template>
  <div class="paging" v-if="paging.pages > 1">

    <template v-if="first_page">
      <a class="paging__item" @click="$emit('changePage', 1)">1</a>...
    </template>

    <a v-for="page in prev_pages"
       class="paging__item"
       @click="$emit('changePage', page)"
    >{{ page }}</a>

    <a class="paging__item paging__active">{{ paging.page }}</a>

    <a v-for="page in next_pages"
       class="paging__item"
       @click="$emit('changePage', page)"
    >{{ page }}</a>

    <template v-if="last_page">
      ...<a class="paging__item" @click="$emit('changePage', paging.pages)">{{ paging.pages }}</a>
    </template>

  </div>
</template>


<script>
  export default {
    props: ['paging'],
    data() {
      return {}
    },

    computed: {
      prev_pages() {
        let list = [];
        let page = this.paging.page - 1;
        while (page > 0 && page > (this.paging.page - this.paging.range - 1)) {
          list.push(page);
          page--;
        }
        return list.reverse();
      },
      next_pages() {
        let list = [];
        let page = this.paging.page + 1;
        while (page <= this.paging.pages && page < (this.paging.page + this.paging.range + 1)) {
          list.push(page);
          page++;
        }
        return list;
      },
      first_page() {
        return !(this.prev_pages.length < this.paging.range
          || this.paging.page === this.paging.range + 1)
      },
      last_page() {
        return !(this.next_pages.length < this.paging.range
          || this.paging.page === this.paging.pages - this.paging.range)
      },
    },

    watch: {
      'paging.page': function (val, oldVal) {
        console.log('watch page', this.paging.page, this.paging.pages);
        let page = 1;
        while (page < this.paging.pages) {
          page++;
          console.log(page);
        }
      }
    },

    mounted() {
    },

    methods: {}

  }
</script>


<style>
</style>
