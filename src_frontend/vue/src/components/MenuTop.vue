<template>
  <div>

    <el-menu :default-active="activeIndex"
             class="menu_top"
             mode="horizontal"
             @select="handleSelect">

      <template v-for="(item, item_key) in menu_set.top">

        <template v-if="'subitems' in item">
          <el-submenu :index="item_key + ''"
                      :class="{'float_right': 'float_right' in item}">
            <template slot="title">
              <i v-if="item.icon" :class="item.icon"></i>
              {{ item.label }}
            </template>
            <template v-for="(subitem, subitem_key) in item.subitems">

              <hr v-if="'split' in subitem" class="menu_top__hr">

              <el-menu-item v-if="'router_name' in subitem && 'params' in subitem"
                            class="menu_top__item"
                            :index="item_key + '-' + subitem_key">
                <router-link tag="a"
                             class="menu_top__a"
                             :key="item_key"
                             :to="{name: subitem.router_name, params: {model_name: subitem.params.model_name}}">
                  <i v-if="subitem.icon" :class="subitem.icon"></i>
                  {{ subitem.label }}
                </router-link>
              </el-menu-item>

              <el-menu-item v-else-if="'router_name' in subitem"
                            class="menu_top__item"
                            :index="item_key + '-' + subitem_key">
                <router-link tag="a"
                             class="menu_top__a"
                             :key="item_key"
                             :to="{name: subitem.router_name}">
                  <i v-if="subitem.icon" :class="subitem.icon"></i>
                  {{ subitem.label }}
                </router-link>
              </el-menu-item>

              <el-menu-item v-else
                            class="menu_top__item"
                            :index="item_key + '-' + subitem_key">
                <a class="menu_top__a" :href="subitem.url">{{ subitem.label }}</a>
              </el-menu-item>

            </template>
          </el-submenu>
        </template>

        <template v-else>

          <el-menu-item v-if="'router_name' in item && 'params' in item"
                        class="menu_top__item"
                        :index="item_key + '-' + item_key">
            <router-link tag="a"
                         class="menu_top__a"
                         :key="item_key"
                         :to="{name: item.router_name, params: {model_name: item.params.model_name}}">
              {{ item.label }}
            </router-link>
          </el-menu-item>

          <el-menu-item v-else-if="'router_name' in item"
                        class="menu_top__item"
                        :index="item_key + ''">
            <router-link tag="a"
                         class="menu_top__a"
                         :key="item_key"
                         :to="{name: item.router_name}">
              {{ item.label }}
            </router-link>
          </el-menu-item>

          <el-menu-item v-else
                        :class="{'float_right': 'float_right' in item}"
                        :index="item_key + ''">
            <a class="menu_top__a" :href="item.url">{{ item.label }}</a>
          </el-menu-item>

        </template>

      </template>

      <el-menu-item v-if="$store.state.deal.permissions.includes('deal.add_deal')">
        <div class="menu_top__deal_add" title="Создать новую сделку" @click="dealAdd">
          <i class="el-icon-document-add"></i>Сделка
        </div>
      </el-menu-item>

      <template v-if="$store.state.deal.settings.sip_id">
        <el-menu-item>
          <div class="sip-get-incoming" title="Список входящих звонков" @click="sipShow(true, 100)">
            <i class="el-icon-notebook-2"></i></div>
        </el-menu-item>
        <el-menu-item>
          <div class="sip-get-incoming" title="Входящий звонок" @click="sipShow(true, 1)">
            <i class="el-icon-phone-outline"></i></div>
        </el-menu-item>
      </template>

      <template v-if="$store.state.deal.settings.mlm_agent">
        <el-menu-item>
          <a href="/partner/" class="partner__link" title="Партнерка"><i class="el-icon-attract"></i></a>
        </el-menu-item>
      </template>

    </el-menu>

    <sip-get :sip_show="sip_show"
             :sip_limit="sip_limit"
             @sipDealAdd="sipDealAdd"
             @sipShow="sipShow"/>

  </div>
</template>


<script>
  export default {
    props: ['menu_set'],
    data() {
      return {
        sip_show: false,
        sip_limit: 1,
        activeIndex: '0',
      }
    },

    computed: {},

    mounted() {
    },

    methods: {
      handleSelect(key, keyPath, el) {
        // console.log('menu_top router:', key, keyPath);
      },
      dealAdd() {
        this.$store.commit('set_deal', {'id': 'add'});
      },

      sipShow(value, limit) {
        limit ? this.sip_limit = limit : 1;
        this.sip_show = value;
      },
      sipDealAdd(phone) {
        this.$store.commit('set_deal', {'id': 'add', 'phone': phone});
      }

    }
  }
</script>


<style>
</style>
