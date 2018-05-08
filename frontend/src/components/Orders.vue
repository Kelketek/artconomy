<template>
  <div class="order-list">
    <v-tabs v-model="tab" fixed-tabs>
      <v-tab href="#tab-current" key="current">
        <v-icon>list</v-icon>&nbsp;Current
      </v-tab>
      <v-tab href="#tab-archived" key="archived">
        <v-icon>archive</v-icon>&nbsp;Archived
      </v-tab>
      <v-tab href="#tab-cancelled" key="cancelled">
        <v-icon>do_not_disturb</v-icon>&nbsp;Cancelled
      </v-tab>
    </v-tabs>
    <v-tabs-items v-model="tab">
      <v-tab-item id="tab-current" v-if="buyer">
        <ac-order-list :url="`${url}current/`" :buyer="buyer" :username="username" />
      </v-tab-item>
      <v-tab-item id="tab-current" v-else>
        <v-tabs v-model="currentTab" fixed-tabs>
          <v-tab href="#tab-store">Store</v-tab>
          <v-tab href="#tab-placeholders">Placeholders</v-tab>
        </v-tabs>
        <v-tabs-items v-model="currentTab">
          <v-tab-item id="tab-store">
            <ac-order-list :url="`${url}current/`" :buyer="buyer" :username="username" />
          </v-tab-item>
          <v-tab-item id="tab-placeholders" :class="{'tab-shown': shownTab('tab-placeholders')}">
            <ac-placeholder-list :url="`${url}current/placeholders/`" :username="username" />
          </v-tab-item>
        </v-tabs-items>
      </v-tab-item>
      <v-tab-item id="tab-archived" v-if="buyer">
        <ac-order-list :url="`${url}archived/`" :buyer="buyer" :username="username" />
      </v-tab-item>
      <v-tab-item id="tab-archived" v-else>
        <v-tabs v-model="archiveTab" fixed-tabs>
          <v-tab href="#tab-store">Store</v-tab>
          <v-tab href="#tab-placeholders">Placeholders</v-tab>
        </v-tabs>
        <v-tabs-items v-model="archiveTab">
          <v-tab-item id="tab-store">
            <ac-order-list :url="`${url}archived/`" :buyer="buyer" :username="username" />
          </v-tab-item>
          <v-tab-item id="tab-placeholders">
            <ac-placeholder-list :url="`${url}archived/placeholders/`" :username="username" />
          </v-tab-item>
        </v-tabs-items>
        <ac-order-list :url="`${url}archived/`" :buyer="buyer" :username="username" />
      </v-tab-item>
      <v-tab-item id="tab-cancelled">
        <ac-order-list :url="`${url}cancelled/`" :buyer="buyer" :username="username" />
      </v-tab-item>
    </v-tabs-items>
  </div>
</template>

<script>
  import Viewer from '../mixins/viewer'
  import Perms from '../mixins/permissions'
  import AcOrderPreview from './ac-order-preview'
  import { paramHandleMap, EventBus } from '../lib'
  import AcOrderList from './ac-order-list'
  import AcPlaceholderList from './ac-placeholder-list'

  export default {
    name: 'Orders',
    mixins: [Viewer, Perms],
    components: {
      AcPlaceholderList,
      AcOrderList,
      AcOrderPreview
    },
    data () {
      return {
        // Used by tab mapper
        query: null
      }
    },
    methods: {
      shownTab (tabName) {
        if (tabName === this.currentTab && this.tab === 'tab-current') {
          EventBus.$emit('tab-shown', tabName)
          return true
        }
      }
    },
    props: ['url', 'buyer'],
    computed: {
      tab: paramHandleMap('tabName', ['subTabName'], undefined, 'tab-current'),
      currentTab: paramHandleMap('subTabName', undefined, ['tab-store', 'tab-placeholders'], 'tab-store'),
      archiveTab: paramHandleMap('subTabName', undefined, ['tab-store', 'tab-placeholders'], 'tab-store'),
      extended () {
        return this.url.indexOf('sales') !== -1
      }
    }
  }
</script>

<style>
  @keyframes delay-display {
    0% { opacity: 0 }
    99% { opacity: 0 }
    100% { opacity: 1 }
  }
  .order-list .btn--floating {
    visibility: hidden;
    opacity: 0;
    transition: none;
  }
  .order-list .tab-shown .btn--floating {
    visibility: visible;
    opacity: 1;
    animation: delay-display 1s;
  }
</style>