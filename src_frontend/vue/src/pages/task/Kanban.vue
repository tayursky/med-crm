<template>

  <div class="kanban">

    <div>
      <el-select v-model="activity" class="kanban__activity_select" filterable>
        <el-option v-for="item in kanban_list"
                   :key="item.value"
                   :label="item.label"
                   :value="item.value">
        </el-option>
      </el-select>

      <el-button icon="el-icon-refresh" class="lime" @click="activityLoad"></el-button>
    </div>

    <div class="kanban__table">
      <div v-for="(step, step_index) in steps"
           class="kanban__step"
           :style="{width: step_width}">
        <div class="kanban__step__mount">
          {{ tasks[step.step].total }} руб.
        </div>

        <div class="kanban__step__head"
             :style="{color: step.color, backgroundColor: step.background}">
          {{ step.name }}
        </div>

        <div class="kanban__step__task_add"
             title="Добавить задачу"
             @click="taskAdd(step_index)">
          <i class="el-icon-plus"></i>
        </div>

        <!-- Task -->
        <div v-for="(task, task_index) in tasks[step.step].items"
             class="kanban__table__item"
             :style="{borderColor: steps[step.step-1].background}">
          <div class="kanban__table__set_step">
            <div v-if="step.step > 1"
                 class="kanban__table__set_step__minus"
                 @click="taskSetStep(task.id, step.step-1)">
              <i class="el-icon-d-arrow-left"></i>
            </div>
            <div v-else class="kanban__table__set_step__empty"></div>

            <div v-if="step.step < steps.length"
                 class="kanban__table__set_step__plus"

                 @click="taskSetStep(task.id, step.step+1)">
              <i class="el-icon-d-arrow-right"></i>
            </div>
          </div>
          <div class="kanban__table__item__cost"
               @click="taskEdit(task)">
            {{ task.cost }} руб.
          </div>
          <div v-for="person in task.persons"
               class="kanban__table__item__txt">
            {{ person }}
          </div>
        </div>

      </div>

    </div>

    <kanban_task
        :root_url="root_url"
        :task="task"
        @closeTask="closeTask"
    >
    </kanban_task>

  </div>

</template>


<script>
  import Vue from 'vue'
  import axios from 'axios'
  import VueAxios from 'vue-axios'
  import Kanban_task from "./Kanban_task";

  Vue.use(VueAxios, axios);

  export default {
    components: {Kanban_task},
    data() {
      return {
        searching: false,
        activity: null,
        kanban_list: [],
        steps: [],
        tasks: {},
        task: {}
      }
    },

    watch: {

      activity: function (value, fromValue) {
        console.log('watch kanban_activity', fromValue, ' > ', value);
        this.activityLoad();
      },
    },

    computed: {
      step_width() {
        return 100 / this.steps.length + '%'
      }
    },

    created() {
    },

    mounted() {
      document.title = 'Канбан';
      this.kanbanInit();
    },

    methods: {

      kanbanInit() {
        this.searching = true;
        Vue.axios.get(this.$store.getters.root_url + 'task/get_activity_list/', {params: {'get': true}})
          .then(response => {
            this.kanban_list = response.data.items;
            this.searching = false;
            // console.log(this.kanban_list);
            this.activity = this.kanban_list[0].value;
          })
          .catch(error => {
            console.log(error);
            this.searching = false;
          })
      },

      activityLoad() {
        this.searching = true;
        let params = {
          'activity': this.activity,
        };
        Vue.axios.get(this.$store.getters.root_url + 'task/kanban/', {params: params})
          .then(response => {
            this.steps = response.data.steps;
            this.tasks = response.data.tasks;
            this.searching = false;
          })
          .catch(error => {
            console.log(error);
            this.searching = false;
          })
      },

      taskSetStep(item_id, set_step) {
        console.log('taskSetStep', item_id, set_step);
        let params = {
          'activity': this.activity,
          'pk': item_id,
          'set_step': set_step
        };
        Vue.axios.get(this.$store.getters.root_url + 'task/kanban/', {params: params})
          .then(response => {
            this.steps = response.data.steps;
            this.tasks = response.data.tasks;
            this.searching = false;
          })
          .catch(error => {
            console.log(error);
            this.searching = false;
          })
      },

      taskAdd(step_index) {
        this.task = {
          'activity_id': this.activity,
          'step': this.steps[step_index],
          'id': 'add',
        };
      },
      taskEdit(task) {
        this.task = task;
      },
      closeTask() {
        console.log('closeTask');
        this.task = {};
        this.activityLoad();
      },

    }
  }
</script>


<style scoped>

</style>
