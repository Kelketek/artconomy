<template>
  <div />
</template>

<script setup lang="ts">
import {useErrorHandling} from '@/mixins/ErrorHandling.ts'

defineExpose(useErrorHandling())
</script>
