<template>
  <v-rating :value="value" @input="update"></v-rating>
</template>

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
