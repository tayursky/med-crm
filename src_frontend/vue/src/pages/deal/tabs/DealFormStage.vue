<template>
  <div class="form-group deal-form__stages">

    <div v-if="stage_focused || stage_focused === 0" class="deal-form__stages__label">
      {{ stages[stage_focused].label }}
    </div>

    <div v-for="(stage, stage_index) in stages"
         class="deal-form__stages__item"
         :key="stage.step"
         :style="{width: stage_witdh,
                  backgroundColor: stage.background_color,
                  color: stage.color,
                  opacity: opacity_list[stage_index]}"
         @mouseenter="stageHover(stage.step)"
         @mouseleave="stageLeave(stage.step)"
         @click="$emit('changeData', 'stage', stage.id)">
    </div>

  </div>
</template>


<script>
  export default {
    props: ['stages', 'current_stage_id'],
    data() {
      return {
        stage_focused: null,
      }
    },

    computed: {
      stage_witdh() {
        return 100 / this.stages.length + '%'
      },
      opacity_list() {
        let opacity_list = [];
        for (let key in this.stages) {
          if (this.stages[key].step <= this.stage_focused) {
            opacity_list.push(1)
          } else {
            opacity_list.push(.1)
          }
        }
        return opacity_list
      },
    },

    watch: {},

    mounted() {
      this.setStage();
    },

    methods: {
      setStage() {
        for (let key in this.stages) {
          if (this.stages[key].id == this.current_stage_id) {
            this.stage_focused = parseInt(key);
            break;
          }
        }
      },
      stageHover(step) {
        this.stage_focused = step;
      },
      stageLeave() {
        for (let key in this.stages) {
          if (this.stages[key].id == this.current_stage_id) {
            this.stage_focused = this.stages[key].step;
          }
        }
      }
    }

  }
</script>


<style>

</style>
