<template>

  <div v-if="title" class="deal-dnd__wrap">
    <drag :transfer-data="id" class="deal-dnd__page-btn">
      <div class="deal-dnd__page-btn__id">{{ title }}</div>
    </drag>
    <el-button class="deal-dnd__page-btn__cancel"
               icon="el-icon-close"
               @click="$store.commit('set_drag_drop', {})"/>
  </div>

</template>


<script>
  import {Drag, Drop} from 'vue-drag-drop';

  export default {
    components: {Drag, Drop},
    data() {
      return {
        deal: {},
      }
    },

    watch: {},

    computed: {
      id() {
        return this.$store.state.deal.drag_drop.id
      },
      title() {
        return this.$store.state.deal.drag_drop.title
      },
    },

    created() {
    },

    mounted() {
    },

    methods: {
    }
  }
</script>


<style scoped>

</style>
