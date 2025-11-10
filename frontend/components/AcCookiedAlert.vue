<template>
  <v-alert v-if="active" v-model="isNew" :type="type" :closable="true">
    <slot />
  </v-alert>
</template>

<script setup lang="ts">
import { deleteCookie, getCookie, setCookie } from "@/lib/lib.ts"
import { computed, ref, watch } from "vue"

const props = withDefaults(
  defineProps<{
    type?: "error" | "success" | "warning" | "info"
    cookie: string
    appears?: Date | null
    expires?: Date | null
  }>(),
  { type: "info", expires: null, appears: null },
)

const isNew = ref(!getCookie(props.cookie))

const active = computed(() => {
  // This value is not reactive-- the message will not suddenly appear unless
  // something else triggers a render.
  const now = new Date()
  if (props.appears && now < props.appears) {
    return false
  }
  if (props.expires && now > props.expires) {
    return false
  }
  return true
})

watch(isNew, (value: boolean) => {
  if (!value) {
    setCookie(props.cookie, "read")
    return
  }
  // Current version should never get here, but we might support this in the future.
  deleteCookie(props.cookie)
})
</script>
