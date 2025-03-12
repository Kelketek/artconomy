<template>
  <div class="flex">
    <v-btn
      icon
      variant="plain"
      size="x-small"
      color="primary"
      class="picker-button"
      @click="launchPicker"
    >
      <v-icon size="x-large" :icon="mdiEyedropper" />
    </v-btn>
    <input ref="picker" v-model="model" type="color" class="picker" />
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue"
import { mdiEyedropper } from "@mdi/js"

const model = defineModel<string>()
const picker = ref<HTMLInputElement | null>(null)

const launchPicker = () => {
  if (!picker.value) {
    return
  }
  picker.value.click()
}
</script>

<style>
.picker {
  display: none;
}
</style>
