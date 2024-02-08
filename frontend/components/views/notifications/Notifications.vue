<template>
  <v-container fluid>
    <v-row no-gutters class="mb-2">
      <v-col>
        <v-card>
          <v-tabs fixed-tabs>
            <v-tab :to="{name: 'CommunityNotifications'}">Community<span v-if="counts.community_count">&nbsp;({{counts.community_count}})</span>
            </v-tab>
            <v-tab :to="{name: 'SalesNotifications'}">Sales/Orders<span
                v-if="counts.sales_count">&nbsp;({{counts.sales_count}})</span></v-tab>
          </v-tabs>
        </v-card>
      </v-col>
    </v-row>
    <router-view :key="$route.path"/>
  </v-container>
</template>

<script lang="ts">
import {Component, mixins, toNative} from 'vue-facing-decorator'
import Viewer from '@/mixins/viewer.ts'
import {ListController} from '@/store/lists/controller.ts'
import AcNotification from '@/types/AcNotification.ts'

@Component({})
class NotificationsCenter extends mixins(Viewer) {

  public community: ListController<
      AcNotification<any, any>> = null as unknown as ListController<AcNotification<any, any>>

  public sales: ListController<
      AcNotification<any, any>> = null as unknown as ListController<AcNotification<any, any>>

  public created() {
    this.community = this.$getList('communityNotifications', {
      grow: true,
      endpoint: '/api/profiles/data/notifications/community/',
    })
    this.sales = this.$getList('salesNotifications', {
      grow: true,
      endpoint: '/api/profiles/data/notifications/sales/',
    })
    this.community.firstRun().catch(this.setError)
    this.sales.firstRun().catch(this.setError)
  }

  public get counts() {
    return this.$store.state.notifications!.stats
  }
}

export default toNative(NotificationsCenter)
</script>
