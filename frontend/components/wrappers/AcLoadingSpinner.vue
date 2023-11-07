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
import {Component, Prop, toNative} from 'vue-facing-decorator'
import {ArtVue} from '@/lib/lib'

@Component
class AcLoadingSpinner extends ArtVue {
  @Prop({default: '50vh'})
  public minHeight!: string
}

export default toNative(AcLoadingSpinner)
</script>
