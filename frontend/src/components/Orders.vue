<template>
  <div class="order-list">
    <v-layout row wrap text-xs-center v-if="stats && !buyer" class="mt-2 mb-2">
      <v-flex xs12 md6>
        <v-layout row wrap>
          <v-flex xs6>Max Load:</v-flex>
          <v-flex xs6>{{stats.max_load}}</v-flex>
          <v-flex xs6>Current Load:</v-flex>
          <v-flex xs6>{{stats.load}}</v-flex>
          <v-flex xs6>Active Orders:</v-flex>
          <v-flex xs6>{{stats.active_orders}}</v-flex>
          <v-flex xs6>New Orders:</v-flex>
          <v-flex xs6>{{stats.new_orders}}</v-flex>
        </v-layout>
      </v-flex>
      <v-flex xs12 md6 v-if="closed">
        <p><strong>You are currently unable to take new commisions because:</strong></p>
        <ul>
          <li v-if="stats.commissions_closed">You have set your 'commissions closed' setting.</li>
          <li v-if="stats.load >= stats.max_load">You have met or exceeded your maximum load. You can increase your maximum load setting to take on more commissions at one time.</li>
          <li v-if="stats.commissions_disabled && stats.new_orders">You have outstanding new orders to process. Please accept or reject the outstanding orders. Outstanding orders must be handled before you are opened up for new commissions.</li>
        </ul>
      </v-flex>
    </v-layout>
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
  import { paramHandleMap, EventBus, artCall } from '../lib'
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
        query: null,
        stats: null
      }
    },
    methods: {
      shownTab (tabName) {
        if (tabName === this.currentTab && this.tab === 'tab-current') {
          EventBus.$emit('tab-shown', tabName)
          return true
        }
      },
      setStats (response) {
        this.stats = response
      },
      refreshStats () {
        if (this.buyer) {
          return
        }
        artCall(`${this.url}stats/`, 'GET', undefined, this.setStats)
      }
    },
    created () {
      EventBus.$on('refresh-sales-stats', this.refreshStats)
      this.refreshStats()
    },
    props: ['url', 'buyer'],
    computed: {
      tab: paramHandleMap('tabName', ['subTabName'], undefined, 'tab-current'),
      currentTab: paramHandleMap('subTabName', undefined, ['tab-store', 'tab-placeholders'], 'tab-store'),
      archiveTab: paramHandleMap('subTabName', undefined, ['tab-store', 'tab-placeholders'], 'tab-store'),
      extended () {
        return this.url.indexOf('sales') !== -1
      },
      closed () {
        return this.stats.commissions_closed || this.stats.commissions_disabled || this.stats.load >= this.stats.max_load
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