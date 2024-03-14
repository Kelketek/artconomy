<template>
  <v-rating :model-value="modelValue" @update:model-value="update"></v-rating>
</template>

<style>
.v-rating .v-icon {
  padding: 0;
}
</style>

<script setup lang="ts">
const props = defineProps<{modelValue: number}>()
const emit = defineEmits<{'update:modelValue': [number]}>()

const update = (val: number|string) => {
  let result: number
  if (typeof val === 'number') {
    result = val
  } else {
    result = parseInt(val, 10)
  }
  emit('update:modelValue', result)
}
</script>
