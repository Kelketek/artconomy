<template>
  <div class="unread-container">
    <v-btn icon size="x-small" color="primary" v-if="!read" top right absolute class="no-mouse badge-pin">
      <v-icon icon="mdi-alert-decagram"/>
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

<script lang="ts">
import {Component, Prop, toNative, Vue} from 'vue-facing-decorator'

@Component
class AcUnreadMarker extends Vue {
  @Prop({required: true})
  public read!: boolean
}

export default toNative(AcUnreadMarker)
</script>
