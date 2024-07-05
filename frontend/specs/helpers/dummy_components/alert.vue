<template>
  <div></div>
</template>

<script setup lang="ts">
import {useAlerts} from '@/mixins/alerts.ts'

const {sendAlert} = useAlerts()
defineExpose({sendAlert})
</script>
