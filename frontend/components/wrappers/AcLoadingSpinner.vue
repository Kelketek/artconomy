<template>
  <v-flex>
    <v-layout column justify-center align-center :style="{'min-height': minHeight}">
      <v-progress-circular
          indeterminate
          :size="70"
          :width="7"
          color="purple"
      ></v-progress-circular>
    </v-layout>
  </v-flex>
</template>

<script lang="ts">
import Vue from 'vue'
import Component from 'vue-class-component'
import {Prop} from 'vue-property-decorator'

  @Component
export default class AcLoadingSpinner extends Vue {
    @Prop({default: '50vh'})
    public minHeight!: string
}
</script>
