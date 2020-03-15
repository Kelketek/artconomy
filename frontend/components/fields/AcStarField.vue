<template>
  <v-rating :value="value" @input="update"></v-rating>
</template>

<style>
  .v-rating .v-icon {
    padding: 0;
  }
</style>

<script lang="ts">
import Vue from 'vue'
import Component from 'vue-class-component'
import {Prop} from 'vue-property-decorator'

@Component
export default class AcStarField extends Vue {
  @Prop({required: true})
  public value!: number

  public update(val: number) {
    this.$emit('input', val)
  }
}
</script>
