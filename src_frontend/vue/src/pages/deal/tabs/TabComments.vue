<template>
  <div class="form_tab tab_comments">
    <div v-if="loading" class="modal-loading"></div>
    <div v-else>
      <div class="buttons">
        <el-button icon="el-icon-document-add" @click="commentEdit({id:'add'})"></el-button>
        <el-button icon="el-icon-refresh" title="Обновить" @click="commentRefresh"/>
      </div>

      <div v-if="item.id" class="el-tabs__form">
        <the-form app_label="directory"
                  model_name="dealcomment"
                  :item="item"
                  :permissions="permissions"
                  @itemRefresh="commentRefresh"
                  @itemClose="commentRefresh"/>
      </div>

      <table v-if="comments.length > 0" class="form_tab__table">
        <thead>
        <tr>
          <td>Время</td>
          <td class="text-right">Источник</td>
          <td>Комментарий</td>
        </tr>
        </thead>
        <tbody>
        <tr v-for="(comment, comment_index) in comments"
            class="comment" :class="{'hover': item.id && item.id === comment.id }"
            @click="commentEdit(comment)">
          <td class="comment__created_at">{{ comment.created_at }}</td>
          <td class="comment__source">
            <template v-if="comment.client">{{ comment.client__cache.full_name }}</template>
            <template v-if="comment.deal">{{ comment.deal__cache.title }}</template>
          </td>
          <td class="comment__text">{{ comment.comment }}</td>
        </tr>
        </tbody>
      </table>

    </div>
  </div>
</template>


<script>
  import Vue from 'vue'
  import axios from 'axios'
  import VueAxios from 'vue-axios'

  Vue.use(VueAxios, axios);

  export default {
    props: ['client', 'deal', 'tab', 'permissions'],
    data() {
      return {
        loading: false,
        comments: [],
        item: {}
      }
    },
    computed: {},

    watch: {
      'item': function (value, fromValue) {
        if (value === null) {
          this.commentRefresh();
        }
      },
    },

    mounted() {
      this.commentRefresh();
    },

    methods: {
      getFormData() {
        return {
          'client': this.client ? this.client.id : null,
          'deal': this.deal ? this.deal.id : null
        }
      },
      commentRefresh() {
        this.loading = true;
        Vue.axios.get(this.$store.getters.root_url + 'deal/comment/', {params: this.getFormData()})
          .then(response => {
            this.item = {};
            this.comments = response.data.comments;
            this.loading = false;
          })
          .catch(error => {
            this.loading = false;
            console.log(error);
          });
      },

      commentEdit(comment) {
        if (comment.id === 'add') {
          comment.client = this.client ? this.client.id : null;
          comment.deal = this.deal ? this.deal.id : null;
        }
        this.item = comment;
      },

    },
  }
</script>


<style>

</style>
