<template>
<v-alert :type="type" v-model="isNew" :closable="true" v-if="active">
  <slot />
</v-alert>
</template>

<script setup lang="ts">
import {deleteCookie, getCookie, setCookie} from '@/lib/lib.ts'
import {computed, ref, watch} from 'vue'

const props = withDefaults(
    defineProps<{type?: "error" | "success" | "warning" | "info", cookie: string, expires?: Date}>(),
    {type: "info"},
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
