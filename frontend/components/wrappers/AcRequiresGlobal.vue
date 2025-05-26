<script setup lang="ts">
import { computed } from "vue"

const props = defineProps<{ global: string }>()
const hasGlobal = computed(() => {
  // @ts-expect-error Literally checking if this is undefined.
  return !!(window[props.global] as any)
})
</script>

<template>
  <slot v-if="hasGlobal" />
  <v-container v-else fluid class="pa-0"></v-container>
  <v-card>
    <v-card-text>
      <v-row
        class="failure-prompt"
        justify="center"
        align-content="center"
        align="center"
      >
        <v-col class="text-center shrink" align-self="center" cols="12">
          <p>
            Your browser is missing a key feature, and we can't display this
            content. This might happen from browsers like the Facebook app's
            built-in browser, or similar embedded browsers. There should be a
            menu at the top or bottom of your screen that has a link to 'Open in
            browser' or 'Open in Safari' or similar.
          </p>
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>
</template>

<style scoped></style>
