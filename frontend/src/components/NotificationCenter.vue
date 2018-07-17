<template>
  <v-layout>
    <v-flex>
      <v-tabs fixed-tabs v-model="tab">
        <v-tab href="#tab-community">Community<span v-if="counts && counts.community_count">&nbsp;({{counts.community_count}})</span></v-tab>
        <v-tab href="#tab-art">Art<span v-if="counts && counts.art_count">&nbsp;({{counts.art_count}})</span></v-tab>
        <v-tab href="#tab-sales">Sales/Orders<span v-if="counts && counts.sales_count">&nbsp;({{counts.sales_count}})</span></v-tab>
      </v-tabs>
      <v-tabs-items v-model="tab">
        <v-tab-item id="tab-community">
          <ac-list-notifications subset="community" class="mt-2" :host-tab="tabName"></ac-list-notifications>
        </v-tab-item>
        <v-tab-item id="tab-art">
          Art
        </v-tab-item>
        <v-tab-item id="tab-sales">
          <ac-list-notifications subset="sales" class="mt-2" :host-tab="tabName"></ac-list-notifications>
        </v-tab-item>
      </v-tabs-items>
    </v-flex>
  </v-layout>
</template>

<script>
  import {EventBus, paramHandleMap} from '../lib'
  import AcListNotifications from './ac-list-notifications'

  export default {
    name: 'NotificationCenter',
    components: {AcListNotifications},
    data () {
      return {
        url: '/api/profiles/v1/data/notifications/',
        counts: null
      }
    },
    computed: {
      tab: paramHandleMap('tabName'),
      tabName () {
        if (this.tab === undefined) {
          return ''
        }
        return this.tab.split('-', 2)[1]
      }
    },
    methods: {
      setCounts (counts) {
        this.counts = counts
      }
    },
    created () {
      EventBus.$on('notification-count', this.setCounts)
    },
    destroyed () {
      EventBus.$off('notification-count', this.setCounts)
    }
  }
</script>