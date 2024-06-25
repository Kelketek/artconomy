<template>
  <v-container fluid>
    <v-tabs fixed-tabs>
      <v-tab :to="{name: 'LinksAndStats', params: {username}}">Referrals</v-tab>
      <v-tab :to="{name: 'Tools', params: {username}}">Tools</v-tab>
    </v-tabs>
    <router-view></router-view>
  </v-container>
</template>

<script setup lang="ts">
import {useRoute, useRouter} from 'vue-router'
import SubjectiveProps from '@/types/SubjectiveProps.ts'

const props = defineProps<SubjectiveProps>()
const route = useRoute()
const router = useRouter()

if (route.name === 'ReferralsAndTools') {
  router.replace({
    name: 'LinksAndStats',
    params: {username: props.username},
  })
}
</script>
