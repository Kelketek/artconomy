<template>
  <v-row no-gutters>
    <v-col cols="12">
      <router-view />
    </v-col>
  </v-row>
</template>

<script setup lang="ts">
import {useRoute, useRouter} from 'vue-router'
import {onMounted} from 'vue'
import type {SubjectiveProps} from '@/types/main'

const props = defineProps<SubjectiveProps>()

const router = useRouter()
const route = useRoute()

onMounted(() => {
  if (route.name === 'Payment') {
    router.replace({
      name: 'Purchase',
      params: {username: props.username},
    })
  }
})
</script>

<style scoped>

</style>
