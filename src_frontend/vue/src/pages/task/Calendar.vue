<template>

  <div class="kanban">

    <h1>Календарь</h1>

    <div>
      <el-select v-model="service"
                 class="kanban__service_select"
                 filterable
                 placeholder=""
      >
        <el-option v-for="item in kanban_list"
                   :key="item.value"
                   :label="item.label"
                   :value="item.value"
        >
        </el-option>
      </el-select>

      <el-button icon="el-icon-refresh" class="lime" @click="kanbanLoad"></el-button>
    </div>

    <div class="kanban__table">
      <div v-for="step in steps"
           class="kanban__step"
           :style="{width: step_width}"
      >
        <div class="kanban__step__mount">
          {{ items[step.step].total }} руб.
        </div>

        <div class="kanban__step__head"
             :style="{color: step.color, backgroundColor: step.background}">
          {{ step.name }}
        </div>


        <div v-for="(item, index) in items[step.step].items"
             class="kanban__table__item"
             :style="{borderColor: steps[step.step-1].background}"
        >
          <div class="kanban__table__set_step">
            <div v-if="step.step > 1"
                 class="kanban__table__set_step__minus"
                 @click="kanbanSetStep(item.id, step.step-1)">
              <i class="el-icon-d-arrow-left"></i>
            </div>
            <div v-else class="kanban__table__set_step__empty"></div>

            <div v-if="step.step < steps.length"
                 class="kanban__table__set_step__plus"

                 @click="kanbanSetStep(item.id, step.step+1)">
              <i class="el-icon-d-arrow-right"></i>
            </div>
          </div>
          <div class="kanban__table__item__cost">{{ item.cost }} руб.</div>
          <div v-for="person in item.persons"
               class="kanban__table__item__txt">
            {{ person }}
          </div>
        </div>

      </div>

    </div>

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
				service: null,
				kanban_list: [],
				steps: [],
				items: {},
			}
		},

		watch: {

			service: function (value, fromValue) {
				console.log('watch kanban_service', fromValue, ' > ', value);
				this.kanbanLoad();
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
			document.title = 'Календарь';
			this.kanbanInit();
		},

		methods: {

			kanbanInit() {
				this.searching = true;
				Vue.axios.get(this.$store.getters.root_url + 'task/get_kanban_list/', {params: {'get': true}})
					.then(response => {
						this.kanban_list = response.data.items;
						this.searching = false;
						console.log(this.kanban_list);
					})
					.catch(error => {
						console.log(error);
						this.searching = false;
					})
			},

			kanbanLoad() {
				this.searching = true;
				let params = {
					'service': this.service,
				};
				Vue.axios.get(this.$store.getters.root_url + 'task/kanban/', {params: params})
					.then(response => {
						this.steps = response.data.steps;
						this.items = response.data.items;
						this.searching = false;
					})
					.catch(error => {
						console.log(error);
						this.searching = false;
					})
			},


			kanbanSetStep(item_id, set_step) {
				console.log('kanbanSetStep', item_id, set_step);
				let params = {
					'service': this.activity,
					'pk': item_id,
					'set_step': set_step
				};
				Vue.axios.get(this.$store.getters.root_url + 'task/kanban/', {params: params})
					.then(response => {
						this.steps = response.data.steps;
						this.items = response.data.items;
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


<style scoped>

</style>
