<template>
  <div
    v-if="value"
    class="hidden-marker-container"
  >
    <v-icon
      class="ml-2 mt-2 elevation-20 background-black"
      :icon="mdiEyeOff"
    />
  </div>
</template>

<script setup lang="ts">
import {mdiEyeOff} from '@mdi/js'
defineProps<{value: boolean}>()
</script>

<style scoped>
.hidden-marker-container {
  position: absolute;
  height: 100%;
  width: 100%;
  z-index: 1;
}

.background-black {
  background-color: #000;
  border-radius: 20px;
}
</style>
