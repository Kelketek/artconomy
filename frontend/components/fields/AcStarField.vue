<template>
  <v-rating :model-value="value" @update:model-value="update"></v-rating>
</template>

<style>
.v-rating .v-icon {
  padding: 0;
}
</style>

<script setup lang="ts">
import {computed} from 'vue'

const props = defineProps<{modelValue?: number|null}>()
const emit = defineEmits<{'update:modelValue': [number]}>()

const value = computed(() => {
  if (typeof props.modelValue === 'number') {
    return props.modelValue
  }
  return undefined
})

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
