<template>
  <div class="unread-container">
    <v-btn icon size="x-small" color="primary" v-if="!read" top right absolute class="no-mouse badge-pin">
      <v-icon :icon="mdiAlertDecagram"/>
    </v-btn>
    <slot></slot>
  </div>
</template>

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

<script setup lang="ts">
import {mdiAlertDecagram} from '@mdi/js'

defineProps<{read: boolean}>()
</script>
