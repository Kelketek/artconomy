<template>
<v-alert :type="type" v-model="isNew" :closable="true">
  <slot />
</v-alert>
</template>

<script setup lang="ts">
import {deleteCookie, getCookie, setCookie} from '@/lib/lib.ts'
import {ref, watch} from 'vue'

const props = withDefaults(
    defineProps<{type?: "error" | "success" | "warning" | "info", cookie: string}>(),
    {type: "info"},
)

const isNew = ref(!getCookie(props.cookie))

watch(isNew, (value: boolean) => {
  if (!value) {
    setCookie(props.cookie, 'read')
    return
  }
  // Current version should never get here, but we might support this in the future.
  deleteCookie(props.cookie)
})
</script>
