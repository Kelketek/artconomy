<template>
  <v-form v-bind="attrs" ref="root">
    <slot />
  </v-form>
</template>

<script setup lang="ts">
import { nextTick, onMounted, ref, useAttrs } from "vue"
import { VForm } from "vuetify/components"

defineOptions({ inheritAttrs: false })
const attrs = useAttrs()
const root = ref<null | typeof VForm>(null)

onMounted(() =>
  nextTick(() =>
    window._paq.push(["FormAnalytics::scanForForms", root.value!.outerHTML]),
  ),
)
</script>
