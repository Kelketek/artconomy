<template>
  <v-icon :icon="value ? mdiCheckCircle : mdiCloseCircle" :color="value ? 'green' : 'red'" />
</template>

<script setup lang="ts">
import {mdiCheckCircle, mdiCloseCircle} from '@mdi/js'

defineProps<{value: boolean}>()
</script>
