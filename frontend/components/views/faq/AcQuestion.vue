<template>
  <v-expansion-panel @group:selected="tweakTag">
    <v-expansion-panel-title>
      <component :is="headerTag" class="text-subtitle-1 font-weight-bold">
        <slot name="title" />
      </component>
    </v-expansion-panel-title>
    <v-expansion-panel-text>
      <slot />
    </v-expansion-panel-text>
  </v-expansion-panel>
</template>

<script setup lang="ts">
import { ref } from "vue"

const headerTag = ref("strong")
const tweakTag = ({ value }: { value: boolean }) => {
  if (value) {
    headerTag.value = "h2"
  } else {
    headerTag.value = "span"
  }
}
</script>
