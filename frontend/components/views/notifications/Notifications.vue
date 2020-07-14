<template>
  <v-container fluid>
    <v-row no-gutters  class="mb-2">
      <v-col>
        <v-tabs fixed-tabs>
          <v-tab :to="{name: 'CommunityNotifications'}">Community<span v-if="counts.community_count">&nbsp;({{counts.community_count}})</span>
          </v-tab>
          <v-tab :to="{name: 'SalesNotifications'}">Sales/Orders<span
              v-if="counts.sales_count">&nbsp;({{counts.sales_count}})</span></v-tab>
        </v-tabs>
      </v-col>
    </v-row>
    <router-view :key="$route.path" />
  </v-container>
</template>

<script lang="ts">
import {paramHandleMap} from '@/lib/lib'
import Component, {mixins} from 'vue-class-component'
import Viewer from '@/mixins/viewer'
import {ListController} from '@/store/lists/controller'
import AcNotification from '@/types/AcNotification'
// import AcListNotifications from './ac-list-notifications'

  @Component
export default class NotificationsCenter extends mixins(Viewer) {
    @paramHandleMap('tabName')
    public tab!: string

    public community: ListController<
      AcNotification<any, any>> = null as unknown as ListController<AcNotification<any, any>>

    public sales: ListController<
      AcNotification<any, any>> = null as unknown as ListController<AcNotification<any, any>>

    public created() {
      this.community = this.$getList('communityNotifications', {
        grow: true, endpoint: '/api/profiles/v1/data/notifications/community/',
      })
      this.sales = this.$getList('salesNotifications', {
        grow: true, endpoint: '/api/profiles/v1/data/notifications/sales/',
      })
      this.community.firstRun().catch(this.setError)
      this.sales.firstRun().catch(this.setError)
    }

    public get counts() {
      return this.$store.state.notifications.stats
    }
}
</script>
