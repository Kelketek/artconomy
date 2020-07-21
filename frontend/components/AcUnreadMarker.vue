<template>
  <div class="unread-container">
    <v-btn fab x-small color="primary" v-if="!read" top right absolute class="no-mouse"><v-icon>new_releases</v-icon></v-btn>
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
</style>

<script lang="ts">
import Vue from 'vue'
import Component from 'vue-class-component'
import {Prop} from 'vue-property-decorator'

@Component
export default class AcUnreadMarker extends Vue {
  @Prop({required: true})
  public read!: boolean
}
</script>
