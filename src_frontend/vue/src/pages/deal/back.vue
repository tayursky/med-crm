  <!-- Group -->
  <el-tooltip v-if="Object.keys(day.groups).indexOf(time.key) > -1"
              class="i-schedule__table__group"
              effect="dark"
              :content="day.groups[time.key].masters_string"
              :disabled="day.groups[time.key].masters.length === 0"
              placement="right-end">
    <el-button>
      <div class="i-schedule__table__group__name">{{ day.groups[time.key].name }}</div>
      <div class="i-schedule__table__group__count">{{ day.groups[time.key].persons }}</div>
    </el-button>
  </el-tooltip>

  <!-- Empty cell -->
  <div v-if="!day.timing[time.key].deals.length"
       @click="dealAdd(day, day.timing[time.key].label, day.timing[time.key].minutes)">
    <drop class="i-schedule__table__time timing_empty"
          :class="{'over': day.label + ' ' + day.timing[time.key].label ===
                        $store.state.deal.drag_drop.datetime}"
          @dragover="dndDragover({datetime: day.label + ' ' + day.timing[time.key].label,
									                                 minutes: day.timing[time.key].minutes })"
          @dragleave="dndResetTime"
          @drop="dndDrop">
      {{ day.timing[time.key].label }}
    </drop>
  </div>

  <template v-for="(cell_key, deals_index) in day.timing[time.key].deals">

    <!-- Empty sub-cell -->
    <div v-if="day.timing[time.key].empty_cells[cell_key]"
         @click="dealAdd(day,
                                         day.timing[time.key].empty_cells[cell_key].label,
                                         day.timing[time.key].empty_cells[cell_key].minutes)">
      <drop class="i-schedule__table__time timing_empty"
            :class="{'over': day.label + ' ' + day.timing[time.key].empty_cells[cell_key].label ===
                          $store.state.deal.drag_drop.datetime}"
            @dragover="dndDragover({
                            datetime: day.label + ' ' + day.timing[time.key].empty_cells[cell_key].label,
									          minutes: day.timing[time.key].empty_cells[cell_key].minutes
									          })"
            @dragleave="dndResetTime"
            @drop="dndDrop">
        {{ day.timing[time.key].empty_cells[cell_key].label }}
      </drop>
    </div>

    <!-- Deal -->
    <div v-if="deals[cell_key]"
         class="i-schedule__table__deal"
         :style="{backgroundColor: service.steps[deals[cell_key].step_number].background_color,
                                color: service.steps[deals[cell_key].step_number].color}"
         @click="dealEdit(deals[cell_key])">
      <el-tooltip class="i-schedule__table__deal__tooltip" effect="dark" placement="right-end">
        <div slot="content">
          <div v-for="person in deals[cell_key].persons">{{ person.string }}</div>
        </div>
        <el-button>
          <drag @drag="dndDrag(deals[cell_key].id)" :transfer-data="deals[cell_key].id"
                class="i-schedule__table__deal__drag">
            <div class="i-schedule__table__deal__time">{{deals[cell_key].start_string }}</div>
            <div class="i-schedule__table__deal__minutes" :class="'pravka_'+deals[cell_key].pravka">
              {{ deals[cell_key].minutes }}
            </div>
            <div class="i-schedule__table__deal__persons">{{ deals[cell_key].persons.length }}</div>
          </drag>
        </el-button>
      </el-tooltip>
    </div>
    <!-- End deal -->

  </template>

