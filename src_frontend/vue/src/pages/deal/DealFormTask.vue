<template>
  <div>

    <div class="modal-loading" v-if="loading"></div>
    <template v-else-if="form">


      <div class="deal-form__history deal-task">

        <!-- Comment -->
        <div class="deal-task__title">
          <div class="deal-task__title__txt">Комментарий</div>
          <el-button class="deal-task__add" icon="el-icon-document-add" @click="commentEdit({id:'add'})"></el-button>
        </div>
        <div v-if="comment_id" class="form-block deal-task__form">
          <div v-for="field_name in comment_form.ordered_fields"
               class="form-group"
               :class="{
                'has-errors': field_name in comment_form.errors,
                'hidden': 'hidden' in comment_form.fields[field_name].widget.attrs}">
            <el-row>
              <el-col :span="10"
                      class="form-block__label"
                      :class="{'required_field': comment_form.fields[field_name]['required']}">
                {{ comment_form.fields[field_name].label }}
              </el-col>

              <el-col :span="14">
                <form-field :field_name="field_name"
                            :fields="comment_form.fields"
                            :data="comment_form.data"
                            @changeData="commentChangeData"/>
              </el-col>

              <div v-if="field_name in comment_form.errors" class="form-block__errors">
                <div v-for="error in comment_form.errors[field_name]" class="form-block__errors__item">{{ error }}</div>
              </div>
            </el-row>
          </div>
          <div class="form-block__footer">
            <template v-if="comment_id">
              <el-button v-if="comment_id!=='add'" type="primary" @click="commentSave('delete')">
                <div class="el-button__text">Удалить</div>
              </el-button>
            </template>
            <el-button type="primary" @click="comment_id=null">
              <div class="el-button__text">Отмена</div>
            </el-button>
            <div class="float-right">
              <el-button type="primary" @click="commentSave('save')">
                <div class="el-button__text">Сохранить</div>
              </el-button>
            </div>
            <div class="clearfix"></div>
          </div>

        </div>
        <!-- End comment -->

        <!-- Task -->
        <div class="deal-task__title">
          <div class="deal-task__title__txt">Задачи</div>
          <el-button class="deal-task__add" icon="el-icon-document-add" @click="taskEdit({id:'add'})"></el-button>
        </div>
        <div v-if="task_id" class="form-block deal-task__form">
          <div v-for="field_name in form.ordered_fields"
               class="form-group"
               :class="{
                'has-errors': field_name in form.errors,
                'hidden': 'hidden' in form.fields[field_name].widget.attrs}"
          >
            <el-row>
              <el-col :span="10"
                      class="form-block__label"
                      :class="{'required_field': form.fields[field_name]['required']}">
                {{ form.fields[field_name].label }}
              </el-col>

              <el-col :span="14">
                <form-field :field_name="field_name"
                            :fields="form.fields"
                            :data="form.data"
                            @changeData="taskChangeData"/>
              </el-col>

              <div v-if="field_name in form.errors" class="form-block__errors">
                <div v-for="error in form.errors[field_name]" class="form-block__errors__item">{{ error }}</div>
              </div>
            </el-row>
          </div>
          <div class="form-block__footer">
            <template v-if="task_id">
              <el-button v-if="task_id!=='add'" type="primary" @click="taskSave('delete')">
                <div class="el-button__text">Удалить</div>
              </el-button>
              <el-button type="primary" @click="task_id=null">
                <div class="el-button__text">Отмена</div>
              </el-button>
              <!--el-button type="primary" @click="taskCancel()">
                <div class="el-button__text">Отменить</div>
              </el-button-->
            </template>
            <div class="float-right">
              <el-button v-if="task_id !== 'add'" type="primary" @click="taskSave('done')">
                <div class="el-button__text">Выполнено</div>
              </el-button>
              <el-button type="primary" @click="taskSave('save')">
                <div class="el-button__text">Сохранить</div>
              </el-button>
            </div>
            <div class="clearfix"></div>
          </div>

        </div>
        <!-- End task -->

        <!-- Tasks -->
        <div class="deal-form__history">
          <div v-for="(task, task_index) in tasks"
               class="deal-form__history__item deal-task__item"
               :class="{'alarm': task.alarm}"
               @click="taskEdit(task)">
            <div class="title">
              <div class="text">{{ task.title }}</div>
              <div class="deal-form__history_user" :title="task.created_user">
                <i class="el-icon-user-solid"></i>
              </div>
              <div class="time">{{ task.time_planned}}</div>
            </div>
            <div class="value"><span v-if="task.comment">{{ task.comment }}</span></div>
          </div>
        </div>
        <!-- End tasks -->


      </div>

      <!-- History -->
      <div class="deal-form__history">
        <div class="deal-form__history__title">
          <div class="deal-form__history__title__txt">История сделки</div>
          <el-button class="deal-form__history__title__add lime" icon="el-icon-refresh" @click="taskLoad()"></el-button>
        </div>
        <div v-for="(item, item_index) in history"
             class="deal-form__history__item">
          <div class="title">
            <div class="text">{{ item.label }}</div>
            <div class="deal-form__history_user" :title="item.history_user">
              <i class="el-icon-user-solid"></i>
            </div>
            <div class="time">{{ item.time_string }}</div>
          </div>
          <div v-if="item.status_text" class="status_text">{{ item.status_text }}</div>
          <div class="value">
            <span v-if="item.old">{{ item.old }} &rarr; </span><span v-if="item.new">{{ item.new }}</span>
          </div>
        </div>
      </div>
      <!-- End history -->

    </template>
  </div>
</template>


<script>
  import Vue from 'vue'
  import axios from 'axios'
  import VueAxios from 'vue-axios'

  Vue.use(VueAxios, axios);

  export default {
    components: {},
    props: ['deal_id', 'with_task_id'],
    data() {
      return {
        loading: true,
        comment_id: null,
        comment_form: {},
        task_id: null,
        tasks: [],
        form: {},
        history: []
      }
    },

    computed: {
    },

    watch: {
      deal_id: function (val, fromVal) {
        // console.log('watch deal_id', val);
        if (val.id) {
          this.taskLoad();
        }
      },
      with_task_id: function (val, fromVal) {
        // console.log('with_task_id', val);
        this.task_id = val;
      },
    },

    mounted() {
      this.task_id = this.with_task_id;
      this.taskLoad();
    },

    methods: {
      taskLoad() {
        this.loading = true;
        let url = this.$store.getters.root_url + 'deal/task/view/';
        // if (this.deal_id === 'add') {
        // 	url += 'create/add/';
        // } else {
        // 	url += 'edit/' + this.deal.id + '/';
        // }
        let params = {
          'get_task': true,
          'deal': this.deal_id,
        };
        Vue.axios.get(url, {params: params})
          .then(response => {
            this.title = response.data.title;
            this.tasks = response.data.tasks;
            this.comment_id = null;
            this.comment_form = response.data.comment_form;
            this.form = response.data.form;
            this.history = response.data.history;
            this.loading = false;
            this.checkTaskData();
          })
          .catch(error => {
            this.loading = false;
            console.log(error);
          });
      },

      checkTaskData() {
        let inside = false;
        if (this.task_id) {
          for (let key in this.tasks) {
            let task = this.tasks[key];
            if (this.task_id == task.id) {
              inside = true;
              this.form.data.title = task.title;
              this.form.data.comment = task.comment;
              this.form.data.time_planned = task.time_planned;
            }
          }
        }
        if (!inside) {
          this.task_id = null;
        }
      },

      getFormData(object) {
        let formData = new FormData();
        formData.append('csrfmiddlewaretoken', this.form.csrf_token);
        formData.append('task', this.task_id);
        Object.keys(object).forEach(
          key => formData.append(key, object[key])
        );
        return formData;
      },

      taskSave(action) {
        let url = this.$store.getters.root_url + 'deal/task/' + action + '/';
        if (action === 'delete' && !confirm('Удалить?')) {
          return
        }
        if (action === 'done') {
          action = 'save';
          this.form.data.status = 'done';
        }
        url += this.task_id && this.task_id !== 'add' ? this.task_id + '/' : '';
        Vue.axios.post(url, this.getFormData(this.form.data))
          .then(response => {
            // console.log(response);
            if (response.data.form && response.data.form.errors) {
              this.form.errors = response.data.form.errors;
            } else {
              this.comment_id = null;
              this.task_id = null;
              this.tasks = response.data.tasks;
              this.form.errors = {};
              this.history = response.data.history;
            }
          })
          .catch(error => {
            console.log(error);
          });
      },

      taskChangeData(key, value) {
        this.form.data[key] = value;
      },
      taskEdit(task) {
        this.task_id = task.id;
        this.form.errors = {};
        if (task.id === null) {
          this.taskLoad();
        } else if (task.id === 'add') {
          this.form.data.time_planned = '';
          this.form.data.status = 'in_work';
          this.form.data.title = '';
          this.form.data.comment = '';
        } else {
          this.form.data.time_planned = task.time_planned;
          this.form.data.status = task.status;
          this.form.data.title = task.title;
          this.form.data.comment = task.comment;
        }
      },

      commentSave(action) {
        let url = this.$store.getters.root_url + 'deal/comment/' + action + '/';
        if (action === 'delete' && !confirm('Удалить?')) {
          return
        }
        url += this.comment_id && this.comment_id !== 'add' ? this.comment_id + '/' : '';
        Vue.axios.post(url, this.getFormData(this.comment_form.data))
          .then(response => {
            if (response.data.form && response.data.form.errors) {
              this.comment_form.errors = response.data.form.errors;
            } else {
              this.taskLoad();
            }
          })
          .catch(error => {
            console.log(error);
          });
      },
      commentChangeData(key, value) {
        this.comment_form.data[key] = value;
      },
      commentEdit(comment) {
        if (comment.id === null) {
          this.taskLoad();
        } else {
          this.comment_id = comment.id;
        }
      }

    }
  }
</script>


<style>

</style>
