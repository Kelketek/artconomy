<template>
  <v-container class="pa-0" fluid>
    <v-tabs fixed-tabs>
      <v-tab :to="{name: 'Watching', params: {username}}">Watching</v-tab>
      <v-tab :to="{name: 'Watchers', params: {username}}">Watchers</v-tab>
    </v-tabs>
    <router-view :key="route.fullPath" class="pt-2"/>
  </v-container>
</template>

<script setup lang="ts">
import {flatten} from '@/lib/lib.ts'
import SubjectiveProps from '@/types/SubjectiveProps.ts'
import {listenForList} from '@/store/lists/hooks.ts'
import {useRoute, useRouter} from 'vue-router'

const props = defineProps<SubjectiveProps>()
const router = useRouter()
const route = useRoute()
listenForList(`${flatten(props.username)}__watching`)
listenForList(`${flatten(props.username)}__watchers`)
if (route.name === 'Watchlists') {
  router.push({
    name: 'Watching',
    params: {username: props.username},
  })
}
</script>
