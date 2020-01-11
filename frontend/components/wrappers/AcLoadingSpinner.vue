<template>
  <v-container fluid class="pa-0">
    <v-row no-gutters :style="{'min-height': minHeight}">
      <v-col class="text-center" align-self="center">
        <v-progress-circular
          indeterminate
          :size="70"
          :width="7"
          color="purple"
        />
      </v-col>
    </v-row>
  </v-container>
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
