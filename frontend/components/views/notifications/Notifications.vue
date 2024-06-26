<template>
  <v-container fluid>
    <v-row no-gutters class="mb-2">
      <v-col>
        <v-card>
          <v-tabs fixed-tabs>
            <v-tab :to="{name: 'CommunityNotifications', params: {username}}">Community<span v-if="counts.community_count">&nbsp;({{counts.community_count}})</span>
            </v-tab>
            <v-tab :to="{name: 'SalesNotifications', params: {username}}">Sales/Orders<span
                v-if="counts.sales_count">&nbsp;({{counts.sales_count}})</span></v-tab>
          </v-tabs>
        </v-card>
      </v-col>
    </v-row>
    <router-view :key="route.path"/>
  </v-container>
</template>

<script setup lang="ts">
import {useErrorHandling} from '@/mixins/ErrorHandling.ts'
import {useList} from '@/store/lists/hooks.ts'
import {useRoute} from 'vue-router'
import SubjectiveProps from '@/types/SubjectiveProps.ts'
import {flatten} from '@/lib/lib.ts'
import {useSingle} from '@/store/singles/hooks.ts'
import {NotificationStats} from '@/types/NotificationStats.ts'
import {computed} from 'vue'

const props = defineProps<SubjectiveProps>()
const route = useRoute()
const community = useList('communityNotifications' + '__' + flatten(props.username), {
  grow: true,
  endpoint: `/api/profiles/account/${props.username}/notifications/community/`,
})
const sales = useList('salesNotifications' + '__' + flatten(props.username), {
  grow: true,
  endpoint: `/api/profiles/account/${props.username}/notifications/sales/`,
})

const {setError} = useErrorHandling()
community.firstRun().catch(setError)
sales.firstRun().catch(setError)

// This might be already defined if we're the current user-- it would be handled by AcNotificationIndicator.
const stats = useSingle<NotificationStats>('notifications_stats__' + flatten(props.username), {endpoint: `/api/profiles/account/${props.username}/notifications/unread/`, x: {
  count: 0,
  community_count: 0,
  sales_count: 0,
}})
// The stats update loop is in AcNotificationIndicator. We don't update it here because then we'd have two loops, and
// we don't really need the stats when a staffer is viewing someone else's notifications.
const counts = computed(() => stats.x as NotificationStats)
// @ts-expect-error
window.stats = stats
</script>
