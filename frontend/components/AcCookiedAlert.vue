<template>
  <v-alert
    v-if="active"
    v-model="isNew"
    :type="type"
    :closable="true"
  >
    <slot />
  </v-alert>
</template>

<script setup lang="ts">
import {deleteCookie, getCookie, setCookie} from '@/lib/lib.ts'
import {computed, ref, watch} from 'vue'

const props = withDefaults(
    defineProps<{type?: "error" | "success" | "warning" | "info", cookie: string, expires?: Date|null}>(),
    {type: "info", expires: null},
)

const isNew = ref(!getCookie(props.cookie))

const active = computed(() => {
  if (!props.expires) {
    return true
  }
  // Note: This new date object is not reactive, so this won't (necessarily) disappear if the date elapses after render.
  return props.expires > new Date()
})

watch(isNew, (value: boolean) => {
  if (!value) {
    setCookie(props.cookie, 'read')
    return
  }
  // Current version should never get here, but we might support this in the future.
  deleteCookie(props.cookie)
})
</script>
