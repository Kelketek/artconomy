<template>
  <v-row no-gutters>
    <v-col cols="12">
      <router-view></router-view>
    </v-col>
  </v-row>
</template>

<script setup lang="ts">
import SubjectiveProps from '@/types/SubjectiveProps.ts'
import {useRoute, useRouter} from 'vue-router'
import {onMounted} from 'vue'

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
