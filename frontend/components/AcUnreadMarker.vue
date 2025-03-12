<template>
  <div class="unread-container">
    <v-btn
      v-if="!read"
      icon
      size="x-small"
      color="primary"
      top
      right
      absolute
      class="no-mouse badge-pin"
    >
      <v-icon :icon="mdiAlertDecagram" />
    </v-btn>
    <slot />
  </div>
</template>

<script setup lang="ts">
import { mdiAlertDecagram } from "@mdi/js"

defineProps<{ read: boolean }>()
</script>

<style>
.unread-container {
  position: relative;
}

.no-mouse {
  pointer-events: none;
}
.badge-pin {
  position: absolute;
  top: 2px;
  right: 2px;
  z-index: 1;
}
</style>
