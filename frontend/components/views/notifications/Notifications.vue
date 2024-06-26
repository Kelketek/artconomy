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

<script setup lang="ts">
import {useErrorHandling} from '@/mixins/ErrorHandling.ts'
import {useList} from '@/store/lists/hooks.ts'
import {computed} from 'vue'
import {useStore} from 'vuex'
import {ArtState} from '@/store/artState.ts'


const store = useStore<ArtState>()
const community = useList('communityNotifications', {
  grow: true,
  endpoint: '/api/profiles/data/notifications/community/',
})
const sales = useList('salesNotifications', {
  grow: true,
  endpoint: '/api/profiles/data/notifications/sales/',
})

const {setError} = useErrorHandling()
community.firstRun().catch(setError)
sales.firstRun().catch(setError)

const counts = computed(() => store.state.notifications!.stats)
</script>
