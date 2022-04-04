<template>
  <div class="hidden-marker-container" v-if="value">
    <v-icon class="ml-2 mt-2">visibility_off</v-icon>
  </div>
</template>

<style scoped>
  .hidden-marker-container {
    position: absolute;
    height: 100%;
    width: 100%;
    z-index: 1;
  }
</style>

<script lang="ts">
import Vue from 'vue'
import Component from 'vue-class-component'
import {Prop} from 'vue-property-decorator'

@Component
export default class AcHiddenFlag extends Vue {
  @Prop({required: true})
  public value!: boolean
}
</script>
